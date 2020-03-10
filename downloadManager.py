from paramiko import SSHClient, AutoAddPolicy
import folderManager_newLib as localFolder
from pathlib import Path as path_manager
from tqdm import tqdm
import logging
import stat

##### Log environment ###############################################################################################################################################
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logs/download_manager.log')
formatter = logging.Formatter('%(asctime)s: %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)
#####################################################################################################################################################################

#####################################################################################################################################################################

# MW 528
PRODUCT_TO_NOT_DOWNLOAD_MW_528 = 'build_product_sdk'
PRODUCT_TO_NOT_DOWNLOAD_MW_524 = 'build_product_sdk'

FOLDERS_TO_NOT_DOWNLOAD = [
    'release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_OTA',
    'release_netbrazil_4tnfx_uhd_hdcp_nasc_production_noOTA',
    'dev_netbrazil_4tnfx_hd_nohdcp_nonasc_integration_alpha', 
    'dev_netbrazil_2tnfx_hd_nohdcp_nonasc_integration',
]

FOLDERS_TO_DOWNLOAD_513 = [
    'tc7430_uclibc_bc_netbrazil_2t_sdk_dota',
    'tc7430_uclibc_bc_netbrazil_2t_release_hdcp_engg_dota',
    'pace7430_uclibc_bc_netbrazil_2t_release_hdcp_engg_dota',
    'pace7430_uclibc_bc_netbrazil_2t_sdk_dota',
    'pace7430_uclibc_bc_netbrazil_3p_release_hdcp_engg_dota',
    'pace7430_uclibc_bc_netbrazil_3p_sdk_dota',
    'humax7430_uclibc_bc_netbrazil_2t_release_hdcp_engg_dota',
    'humax7430_uclibc_bc_netbrazil_2t_sdk_dota',
    'humax7430_uclibc_bc_netbrazil_3p_release_hdcp_engg_dota',
    'humax7430_uclibc_bc_netbrazil_3p_sdk_dota'
]
#Ideia: limpar toda a string de uclibc / bc / netbrazil / sdk / dota / release / hdcp / engg
#Depois separo em um array os dois valores restantes: modelo e tuner 
#Crio as pastas locais com base nessa info e crio dicionário para os modelos (e.g. humax7430 == HUMAX)
#com o array basta criar os loops e controle


FILES_TO_NOT_DOWNLOAD = [
    'otv5_loader_kernel_squashfs_eng.bin.hdf',
    'otv5_loader_kernel_squashfs.bin.hdf',
    'rootfs.squashfs'
]


#####################################################################################################################################################################

def getBuildNameFromDir(build_path):
    # Server pattern: 'Build6.x.x.x_0123456/'
    # After clean it: '6.x.x.x_0123456'
    return path_manager(''.join(''.join(str(build_path).split('Build')).split('/')))

def ngCleanModelName(model):
    # Should remove: uclibc / bc / netbrazil / sdk / dota / release / hdcp / engg
    # Return list with Model / Tuner (Humax, 2T)
    words_to_remove = [
        'UCLIBC',
        'BC',
        'NETBRAZIL',
        'SDK',
        'DOTA',
        'RELEASE',
        'HDCP',
        'ENGG'
    ]
    
    model_dict = {
        'TC7430' : 'Tech',
        'PACE7430' : 'Pace',
        'HUMAX7430' : 'Humax'
    }
    
    model_and_tuner = ''.join((str(model).upper())).split('_')
    
    for word in list(model_and_tuner):
        if word in words_to_remove:
            model_and_tuner.remove(word)    

    model_and_tuner[0] = model_dict.get(model_and_tuner[0])
    
    return model_and_tuner


def startPathCreator(client, PATH_MW, STB_MODEL, local_build_folder, MW_VERSION):
    is_folder_zip = False #MW 5.2.4 could be zip or not 
    sftp = client.open_sftp()
    if(STB_MODEL):
        build_path = PATH_MW / STB_MODEL # /nfs/OpentvOS/v5.x.x/NET/Build6.x.x.x/brand/
        
    elif not(STB_MODEL):
        build_path = PATH_MW
        
    print('Path:', build_path.as_posix())
    log.info(f'Path created to start download process: {build_path} ')
    #build_name_clean = getBuildNameFromDir(build_name) # Take build name without unnecessary words to persist on Build Number Control (txt)

    try:
        if(MW_VERSION.name == 'v5.2.8'):
            ### Handling MW 528 ###
            #Get all Build_Production_XPTO folders (without attributes) from sftp (MW 5.2.8 only)
            path_product_folder = []
            for folders in sftp.listdir_attr(build_path.as_posix()):
                if not(folders.filename == PRODUCT_TO_NOT_DOWNLOAD_MW_528):
                    path_product_folder.append(folders.filename)

            new_local_path = path_manager(localFolder.createLocalFolders(local_build_folder, STB_MODEL)) # STB Model folder
                
            # Loop to create all Build_Production_XPTO 
            for folder in path_product_folder:
                localFolder.createLocalFolders(new_local_path, folder)

            # Create local sub-folders from Build_Production_XPTO
            # /nfs/OpentvOS/v5.2.8/NET/build_name/STB_Model/build_production_XPTO
            for folder in path_product_folder:
                createLocalSubDirectories(sftp, path_manager.joinpath(build_path, path_manager(folder)).as_posix(), path_manager.joinpath(new_local_path, folder), MW_VERSION, is_folder_zip)
        
        elif(MW_VERSION.name == 'v5.2.4'):
            ### Handling MW 524 ###
            #Check if is a file compacted or a folder 
            path_product_folder = []
                    
            for folders in sftp.listdir_attr(build_path.as_posix()):
                if(stat.S_ISREG(folders.st_mode)):
                    is_folder_zip = True
                              
                elif(stat.S_ISDIR(folders.st_mode)):
                    if not(folders.filename == PRODUCT_TO_NOT_DOWNLOAD_MW_524):
                        path_product_folder.append(folders.filename)
            
            if(is_folder_zip):
                downloadFiles(sftp, local_build_folder, build_path, MW_VERSION, is_folder_zip)
            
            if not(is_folder_zip):
                new_local_path = path_manager(localFolder.createLocalFolders(local_build_folder, STB_MODEL)) # STB Model folder
            
                for folder in path_product_folder:
                    localFolder.createLocalFolders(new_local_path, folder)

                # Create local sub-folders from Build_Production_XPTO
                # /nfs/OpentvOS/v5.2.8/NET/build_name/STB_Model/build_production_XPTO
                for folder in path_product_folder:
                    createLocalSubDirectories(sftp, path_manager.joinpath(build_path, path_manager(folder)).as_posix(), path_manager.joinpath(new_local_path, folder), MW_VERSION, is_folder_zip)
                    
                    
        elif(MW_VERSION.name == 'v5.1.3'): 
            path_folders = []
                              
            for folders in sftp.listdir_attr(build_path.as_posix()):
                if(stat.S_ISREG(folders.st_mode)):
                    is_folder_zip = True
                              
                elif(stat.S_ISDIR(folders.st_mode)):
                    if (folders.filename in FOLDERS_TO_DOWNLOAD_513):
                        path_folders.append(folders.filename)
            
            if(is_folder_zip):
                downloadFiles(sftp, local_build_folder, build_path, MW_VERSION, is_folder_zip)

            if not(is_folder_zip):
                folders_dict, remote_path = createSubDirectories513(sftp, local_build_folder, build_path)
                for remote_dir in remote_path:
                    model = ngCleanModelName(remote_dir.name)
                    new_local_path = path_manager(localFolder.createLocalFolders(folders_dict.get(''.join(model)), remote_dir.name))
                    downloadFiles(sftp, new_local_path, remote_dir, MW_VERSION, is_folder_zip)                        
            
    except (EnvironmentError, IOError, OSError) as e:
        print(e)
        log.exception('An error occured to start download process')
        
        
def createSubDirectories513(sftp, local_path, remote_path):
    sub_folders_513_dict = {}
    remote_list = []
    for model_folder in sftp.listdir_attr(remote_path.as_posix()):
        if(model_folder.filename in FOLDERS_TO_DOWNLOAD_513):
            model = ngCleanModelName(model_folder.filename)
            remote_list.append(path_manager.joinpath(path_manager(remote_path), model_folder.filename))
            if not(''.join(model) in sub_folders_513_dict):
                
                if(path_manager.joinpath(local_path, model[0]).exists()):
                    sub_folders_513_dict[''.join(model)] = path_manager(localFolder.createLocalFolders(path_manager.joinpath(local_path, model[0]), model[1]))
                    
                else:
                    sub_folders_513_dict[''.join(model)] = path_manager(localFolder.createLocalFolders(localFolder.createLocalFolders(local_path, model[0]), model[1]))
    
    return sub_folders_513_dict, remote_list

def createLocalSubDirectories(sftp, remote_dir, local_path, MW_VERSION, is_folder_zip):
    current_path = []
    remote_path = []
        
    for dir in sftp.listdir_attr(remote_dir):
        if dir.filename not in FOLDERS_TO_NOT_DOWNLOAD: 
            current_path.append(path_manager(localFolder.createLocalFolders(local_path, dir.filename)))
            remote_path.append(path_manager.joinpath(path_manager(remote_dir), dir.filename))

    return downloadFiles(sftp, current_path, remote_path, MW_VERSION, is_folder_zip)
    
def downloadFiles(sftp, current_path, remote_path, MW_VERSION, is_folder_zip):
    file_name_for_progress_bar = "" # Not necessary, just a improve to progress bar
    callback_progressbar, progressbar = progressBarView(ascii=False, desc=file_name_for_progress_bar, unit='b', unit_scale=True)
    
    # MW 5.2.8 has same folder structure since first version. 
    if(MW_VERSION.name == 'v5.2.8'):
        i = 0 # To control the current_path folders list
        for remote_dir in remote_path:
            print(remote_dir)
            for remote_file in sftp.listdir_attr(remote_dir.as_posix()):
                file_name_for_progress_bar = remote_file.filename
                # CAROUSEL names changes every new build
                # The code below will avoid to download this file.
                
                is_carousel = remote_file.filename.split('-')# CAROUSEL is the first word on filename                          
                if remote_file.filename not in FILES_TO_NOT_DOWNLOAD and not is_carousel[0] == 'CAROUSEL':
                    print(remote_file.filename)
                    sftp.get(path_manager.joinpath(remote_dir, remote_file.filename).as_posix(), path_manager.joinpath(current_path[i], remote_file.filename), callback_progressbar)     
            log.info(f'Files downloaded:{path_manager.joinpath(current_path[i], remote_file.filename)}')
            i += 1
        progressbar.close()
    
    # MW 5.2.4 could have zip folder 
    elif(MW_VERSION.name == 'v5.2.4' and is_folder_zip == True):
        for remote_file in sftp.listdir_attr(remote_path.as_posix()):
            if remote_file.filename not in FILES_TO_NOT_DOWNLOAD:
                print(remote_file.filename)
                sftp.get(path_manager.joinpath(remote_path, remote_file.filename).as_posix(), path_manager.joinpath(current_path, remote_file.filename), callback_progressbar) 
        
                log.info(f'Files downloaded:{path_manager.joinpath(current_path, remote_file.filename)}')
        progressbar.close()
    
    # Scenario that cover MW 5.2.4 when doesn't have zip folder
    
    elif(MW_VERSION.name == 'v5.2.4' and is_folder_zip == False):
        for remote_dir in remote_path:
            print(remote_dir)
            for remote_file in sftp.listdir_attr(remote_dir.as_posix()):
                file_name_for_progress_bar = remote_file.filename            
                if remote_file.filename not in FILES_TO_NOT_DOWNLOAD:
                    print(remote_file.filename)
                    sftp.get(path_manager.joinpath(remote_dir, remote_file.filename).as_posix(), path_manager.joinpath(current_path[i], remote_file.filename), callback_progressbar)     
            log.info(f'Files downloaded:{path_manager.joinpath(current_path[i], remote_file.filename)}')
            i += 1
        progressbar.close()
        
    elif(MW_VERSION.name == 'v5.1.3'):    
        for remote_file in sftp.listdir_attr(remote_path.as_posix()): 
            if str(remote_file.filename) not in FILES_TO_NOT_DOWNLOAD:
                print(path_manager.joinpath(current_path, remote_file.filename))
                sftp.get(path_manager.joinpath(path_manager(remote_path), remote_file.filename).as_posix(), 
                        path_manager.joinpath(current_path, remote_file.filename), 
                        callback_progressbar)                
    
        log.info(f'Files downloaded:{path_manager.joinpath(current_path, remote_file.filename)}') 
        progressbar.close()
            
def progressBarView(*args, **kwargs):
    try:
        progressbar = tqdm(*args, **kwargs)  # Receive N args
        last = [0]  # Last iteration
        def viewBar(a, b):
            progressbar.total = int(b)
            progressbar.update(int(a - last[0]))  # update pbar with increment
            last[0] = a  # update last known iteration
        return viewBar, progressbar  # return callback, tqdmInstance   
        
    except Exception as e:
        print('Error:',e)   
        log.exception('An error occured to use progress bar function')      


def startDownloadProcess(PATH_ROOT, MW_VERSION, STB_MODEL, NET, client, latestBuild_path, local_build_folder):

        PATH_MW = path_manager.joinpath(PATH_ROOT, MW_VERSION, NET, latestBuild_path) #/nfs/OpentvOS/v5.x.x/NET/Build6.x.x.x
        startPathCreator(client, PATH_MW, STB_MODEL, local_build_folder, MW_VERSION)