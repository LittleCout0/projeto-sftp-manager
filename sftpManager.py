from downloadManager import startDownloadProcess as download
from paramiko import SSHClient, AutoAddPolicy
from pathlib import Path as path_manager
import fileManager as localFile
import folderManager as localFolder
import logging

##### Connection  ###############################################################################################################################################
HOST = 'zrhftp.hq.k.grp'
USER = 'wsouza'
PWORD = 'Willi@m.07'
PORT = 22

##### Variables  ###############################################################################################################################################
ROOT = path_manager('/nfs/OpentvOS')
NET = path_manager('NET')
MW_VERSION_513 = path_manager('v5.1.3')
MW_VERSION_524 = path_manager('v5.2.4')
MW_VERSION_528 = path_manager('v5.2.8')
STB_MW_528_LIST = [
    'dgci362_unified_glibc_bc', 
    'dci738net_glibc_bc'
]
MW_VERSION_LIST = [MW_VERSION_528, MW_VERSION_524, MW_VERSION_513]

##### Log ###############################################################################################################################################
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logs/sftpManager.log')
formatter = logging.Formatter(
    '%(asctime)s: %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)
#####################################################################################################################################################################

def connectionToServer():
    try:
        client = SSHClient()
        print('Connecting to', HOST)
        log.info('Connecting to server')
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(HOST, PORT, username=USER, password=PWORD)
        print('Connection established!')
        log.info('Connection established')
        return client
    except (Exception) as e:
        print('Not possible to connect. Error:', e)
        log.exception('An error occured to connect in Zurich server')
        return False


def getLatestBuildDownloadLocally(latest_build, MW_VERSION):
    status = localFile.pathControl(latest_build, MW_VERSION)

    '''
    0 - Go ahead and download
    1 - It's already downloaded
    2 - Go ahead to download it and create a Version control since it wasn't created yet
    3 - Fail
    '''

    if status == 0:
        # Go ahead and download
        log.info('Status == 0. Go ahead and download')
        return True

    elif status == 1:
        # It's already downloaded
        log.info('Status == 1. It is already downloaded')
        return False

    elif status == 2:
        # Go ahead and download. Version control wasn't created yet
        log.info(
            'Status == 2. Go ahead and download. Version control was not created yet')
        return True

    elif status == 3:
        # Fail
        print('Please check if Version_control folder exists')
        log.error('Status == 3. Fail (Version_control folder exist?).')
        return False

def getLatestBuildNameFromServer(client, PATH_MW):
    # Compare Modification time folder by folder
    sftp = client.open_sftp()
    try:
        dir_MW = sftp.listdir_attr(PATH_MW.as_posix())
        log.info(f'Getting latest modified folder from {dir_MW}')
        latest = 0
        latest_folder = None
        
        # Checking if a NET folder is there. Sometimes Build team put a folder with this name
        for folder_attribute in sftp.listdir_attr(PATH_MW.as_posix()):
            if ('NET' in str(folder_attribute.filename).split('_') and folder_attribute.st_mtime > latest):
                dir_MW = path_manager.joinpath(path_manager.joinpath(PATH_MW, folder_attribute.filename))
                 
        for folder_attribute in  sftp.listdir_attr(dir_MW.as_posix()):
            if folder_attribute.st_mtime > latest:
                latest = folder_attribute.st_mtime  # Flag from Paramiko lib: Modification Time
                latest_folder = folder_attribute.filename
        log.info(f'Latest modified folder: {latest_folder}')
        return path_manager(latest_folder)

    except (EnvironmentError, IOError, OSError) as e:
        print(e)
        log.exception('An error occured to get latest build from server')

def getBuildNameFromDir(build_path):
    # Server pattern: 'Build6.x.x.x_0123456/'
    # After clean it: '6.x.x.x_0123456'
    return path_manager(''.join(''.join(str(build_path).split('Build')).split('/')))

if __name__ == '__main__':
    client = connectionToServer()
    if(client):
        for MW in MW_VERSION_LIST:
            if(MW == MW_VERSION_528):
                latestBuild_path = getLatestBuildNameFromServer(client, path_manager.joinpath(ROOT, MW_VERSION_528, NET)) #Receive the build path: Build6.x.x.x
                latestBuild_clean = getBuildNameFromDir(latestBuild_path) #Remove "Build" from name to create folder locally: 6.x.x.x
                status = getLatestBuildDownloadLocally(str(latestBuild_clean), MW_VERSION_528)
                if(status):
                    local_build_folder = localFolder.createBuildNameFolder(latestBuild_clean, MW_VERSION_528)
                    for model in STB_MW_528_LIST:
                        print(f'Latest Build from {MW} and {model}: {latestBuild_clean}')
                        log.info(f'Latest Build from {MW} and {model}: {latestBuild_clean}')
                        download(ROOT, MW_VERSION_528, model, NET, client, latestBuild_path, local_build_folder)
                    
                    localFile.createFileControl(latestBuild_clean, MW_VERSION_528)
                    print('Control file created')   
                
            elif(MW == MW_VERSION_524):
                latestBuild_path = getLatestBuildNameFromServer(client, path_manager.joinpath(ROOT, MW_VERSION_524, NET)) #Receive the build path: Build4.x.x.x
                latestBuild_clean = getBuildNameFromDir(latestBuild_path) #Remove "Build" from name to create folder locally: 4.x.x.x
                status = getLatestBuildDownloadLocally(str(latestBuild_clean), MW_VERSION_524)
                if(status):
                    local_build_folder = localFolder.createBuildNameFolder(latestBuild_clean, MW_VERSION_524)
                    print(f'Latest Build from {MW}: {latestBuild_clean}')
                    log.info(f'Latest Build from {MW}: {latestBuild_clean}')
                    download(ROOT, MW_VERSION_524, '', NET, client, latestBuild_path, local_build_folder)
                    localFile.createFileControl(latestBuild_clean, MW_VERSION_524)
                    print('Control file created')
            
            elif(MW == MW_VERSION_513):
                latestBuild_path = getLatestBuildNameFromServer(client, path_manager.joinpath(ROOT, MW_VERSION_513, NET)) #Receive the build path: Build2.x.x.x
                latestBuild_clean = getBuildNameFromDir(latestBuild_path) #Remove "Build" from name to create folder locally: 2.x.x.x
                status = getLatestBuildDownloadLocally(str(latestBuild_clean), MW_VERSION_513)
                if(status):
                    local_build_folder = localFolder.createBuildNameFolder(latestBuild_clean, MW_VERSION_513)
                    print(f'Latest Build from {MW}: {latestBuild_clean}')
                    log.info(f'Latest Build from {MW}: {latestBuild_clean}')
                    download(ROOT, MW_VERSION_513, '', NET, client, latestBuild_path, local_build_folder)
                    localFile.createFileControl(latestBuild_clean, MW_VERSION_513)
                    print('Control file created')
                    print('Finished')
    else:
        print('Finishing script...')
    
    client.close()