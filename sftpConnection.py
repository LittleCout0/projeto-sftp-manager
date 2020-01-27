
from paramiko import SSHClient, AutoAddPolicy
import fileManager_newLib as localFile
import folderManager_newLib as localFolder
from tqdm import tqdm
from stat import S_ISDIR, S_ISREG
from pathlib import Path as path_manager

HOST = 'zrhftp.hq.k.grp'
USER = 'wsouza'
PWORD = 'Willi@m.07'
PORT = 22


PATH = path_manager('C:/Users/William/Desktop/SFTP Project')
PATH_MW = path_manager('v5.2.8') # var para teste. Usar essa variável para altera o MW que queremos acessar
PATH_MW_528 = path_manager('/nfs/OpentvOS/v5.2.8/NET')
BUILD_MW_528 = '' # var para teste. Usar essa variável para guardar última build alterada na lista 
STB_MODEL_MW_528 = path_manager('dgci362_unified_glibc_bc') # var para teste. Usar esta variável para alterar qual Brand usar (Tech ou Sagem))
FLAVOR_TYPE_MW_528 = path_manager('build_product_release') #var para teste. Usar esta variável para alterar qual tipo vamos baixar (REL, SDK ou DEV)
FLAVOR_SUBTYPE_MW_528 = path_manager('release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_noOTA') #var para teste. Usar esta variável para alterar qual sub pasta vamos baixar
LATEST_BUILD_MODIFIED = ''#variável necessária para saber se já baixamos ou não
# PATH_COMPLETE = PATH_MW_528 + BUILD_MW_528 + STB_MODEL_MW_528 + FLAVOR_TYPE_MW_528 + FLAVOR_SUBTYPE_MW_528

def connectionToServer():
    try:
        client = SSHClient()
        print('Connecting to', HOST)
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(HOST, PORT, username=USER, password=PWORD)
        print('Connection established!')
        return client
    except (Exception) as e:
        print('Connection failed. Error:',e)
        client.close
        return False
        #Possivelmente tenha que chamar de novo a conexão visto que toda vez que usamos "WITH" 
        # Ele cuida de fechar as conexões após rodar o bloco de código
            
def getLatestBuildNameFromServer(client):
    sftp = client.open_sftp()
    try:   
        dir_MW_528 = sftp.listdir_attr(PATH_MW_528.as_posix())
        latest = 0
        latest_folder = None
        #print('Filtrando último arquivo modificado em:', PATH_MW_528)
        for folder_attribute in dir_MW_528:
            if folder_attribute.st_mtime > latest:
                #latest = folder_attribute.st_mtime
                latest_folder = folder_attribute.filename
        return path_manager(latest_folder)

    except (EnvironmentError, IOError, OSError) as e:
        print(e)

def getLatestBuildDownloadLocally(latest_build):
    if(localFile.pathControl(latest_build)) == 0:
        print('Please check if Version_control folder exists')
        return 0
    elif(localFile.pathControl((latest_build, STB_MODEL_MW_528)) == False):
        # Pode baixar
        return True
    elif(localFile.pathControl((latest_build, STB_MODEL_MW_528)) == True):
        # Já tem baixado
        return False       

def getBuildNameFromDir(build_path):
    # Elimina o PATH e mantém somente o Build_name
    #build_name = ''.join(''.join(build_path.split('Build')).split('/')) 
    return path_manager(''.join(''.join(str(build_path).split('Build')).split('/')))

def progressBarView(*args, **kwargs):
    try:
        progressbar = tqdm(*args, **kwargs)  # Recebe N argumentos 
        last = [0]  # Ultima iteração 
        def viewBar(a, b):
            progressbar.total = int(b)
            progressbar.update(int(a - last[0]))  # update pbar with increment
            last[0] = a  # update last known iteration
        return viewBar, progressbar  # return callback, tqdmInstance   
        
    except Exception as e:
        print('Error:',e)         

# quero somente as pastas .. depois criar outro para baixar de cada pasta que eu receber tudo que tiver lá
def listDirectory(sftp, remote_dir, local_path):
    for dir in sftp.listdir_attr(remote_dir.as_posix()):
        remotepath = path.manager(remote_dir)
        type = dir.st_mode 
        if S_ISDIR(type):
            localFolder.createLocalFolders(local_path, dir.filename)
            remotepath = remote_dir / dir.filename            
            return listDirectory(sftp, remotepath, local_path)
        elif type == None:
            return 'None: '+type
        elif S_ISREG(type):
            return remotepath

def createLocalDirectories(sftp, remote_dir, local_path):
    current_path = []
    remote_path = []
    for dir in sftp.listdir_attr(remote_dir):
        current_path.append(path_manager(localFolder.createLocalFolders(local_path, dir.filename)))
        remote_path.append(path_manager.joinpath(path_manager(remote_dir), dir.filename))

    return downloadFiles(sftp, current_path, remote_path)
    
def downloadFiles(sftp, current_path, remote_path):
    file_name_for_progress_bar = ""
    callback_progressbar, progressbar = progressBarView(ascii=False, desc= file_name_for_progress_bar, unit='b', unit_scale=True)
    i = 0
    for remote_dir in remote_path:
        print(remote_dir)
        for remote_file in sftp.listdir_attr(remote_dir.as_posix()):
            file_name_for_progress_bar = remote_file.filename
            sftp.get(path_manager.joinpath(remote_dir, remote_file.filename).as_posix(), path_manager.joinpath(current_path[i], remote_file.filename), callback_progressbar)
        i += 1
    progressbar.close()


def downloadLatestBuild(client, build_name):
    sftp = client.open_sftp()
    build_path = PATH_MW_528 / build_name / STB_MODEL_MW_528 # /nfs/OpentvOS/v5.2.8/NET/build_name/dgci362_unified_glibc_bc/
    print('Path:', build_path.as_posix())
    build_name_clean = getBuildNameFromDir(build_name) # Take build name without unnecessary words to persist on Build Number Control (txt)
    
    try:
        #Get all Build_Production_XPTO folders (without attributes) from sftp
        path_product_folder = []
        for folders in sftp.listdir_attr(build_path.as_posix()):
            path_product_folder.append(folders.filename)
        
        new_local_path = path_manager.joinpath(PATH, localFolder.createBuildNameFolder(build_name_clean)) # Folder with build name clean
        new_local_path = path_manager(localFolder.createSTBModelFolder(new_local_path, STB_MODEL_MW_528)) # Folder of STB Model (dgci362_unified_glibc_bc)
        
        # Loop to create all Build_Production_XPTO 
        for folder in path_product_folder:
            localFolder.createBuildTypeFolder(new_local_path, folder)

        # Create local sub-folders from Build_Production_XPTO
        # /nfs/OpentvOS/v5.2.8/NET/build_name/dgci362_unified_glibc_bc/
        for folder in path_product_folder:
            x = createLocalDirectories(sftp, path_manager.joinpath(build_path, path_manager(folder)).as_posix(), path_manager.joinpath(new_local_path, folder))
            print(x)

    except (EnvironmentError, IOError, OSError) as e:
        print(e)


if __name__ == '__main__':
    
    client = connectionToServer()
    if (client == False):
        print('Finishing script...')

    else:
        latestBuild = getLatestBuildNameFromServer(client)
        print('Latest Build from Server:', latestBuild)
        downloadLatestBuild(client, latestBuild)
        
'''
    client = connectionToServer()
    if (client == False):
        print('Finishing script...')
        

    else:
        latestBuild = getLatestBuildNameFromServer(client)
        print('Latest Build from Server:', latestBuild)
        
        if(getLatestBuildDownloadLocally(latestBuild) == True):
            downloadLatestBuild(client, latestBuild)        
        
        elif(getLatestBuildDownloadLocally(latestBuild) == latestBuild):
            downloadLatestBuild(client, latestBuild)    

        elif(getLatestBuildDownloadLocally(latestBuild) == False):
            print('Finishing script...')
            client.close()
        
        else:
            print('Finishing script...')
            client.close()
    client.close()'''
