from paramiko import SSHClient, AutoAddPolicy
import fileManager_newLib as localFile
import folderManager_newLib as localFolder
from tqdm import tqdm
import os
from pathlib import Path as path_manager

HOST = 'zrhftp.hq.k.grp'
USER = 'wsouza'
PWORD = 'Willi@m.07'
PORT = 22

######################################################################################################################################################################

# VARs to change PATHs and download others Brands and/or MWs

STB_BRAND_528_SAGEM = 'dgci362_unified_glibc_bc'
STB_BRAND_528_TECH = 'dci738net_glibc_bc'
MW_VERSION_513 = 'v5.1.3'
MW_VERSION_524 = 'v5.2.4'
MW_VERSION_528 = 'v5.2.8'
PATH_NET_FOLDER = 'NET'

# MW 528
PRODUCT_TO_NOT_DOWNLOAD_MW_528 = 'build_product_sdk'

# SAGEM MW 528 
FILES_TO_NOT_DOWNLOAD = [
    'CAROUSEL-net-dgci362_otv5_loader_kernel_squashfs_FWver-0x6127_PID-0x1D76_usageID-0x01to0x0A.ts',
    'rootfs.squashfs',
    'otv5_loader_kernel_squashfs.bin',
    'DGCI362_IMAGE', 
    'ubifs-128k-2048-7260a0.img',
    'rootfs.tar.bz2'
]

FOLDERS_TO_NOT_DOWNLOAD = [
    'release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_OTA',
    'release_netbrazil_4tnfx_uhd_hdcp_nasc_production_noOTA',
    'dev_netbrazil_4tnfx_hd_nohdcp_nonasc_integration_alpha', 
    'dev_netbrazil_4tnfx_uhd_hdcp_nonasc_integration'
]

#####################################################################################################################################################################

PATH_MW_528 = path_manager('/nfs/OpentvOS/v5.2.8/NET') # hardcoded to test MW 528
STB_MODEL_MW_528 = path_manager('dgci362_unified_glibc_bc') # hardcoded to test MW 528

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
            
def getLatestBuildNameFromServer(client):

    # Compare Modification time folder by folder
    sftp = client.open_sftp()
    try:   
        dir_MW_528 = sftp.listdir_attr(PATH_MW_528.as_posix())
        latest = 0
        latest_folder = None

        for folder_attribute in dir_MW_528:
            if folder_attribute.st_mtime > latest:
                latest = folder_attribute.st_mtime # Flag from Paramiko lib: Modification Time 
                latest_folder = folder_attribute.filename
        return path_manager(latest_folder)

    except (EnvironmentError, IOError, OSError) as e:
        print(e)

def getLatestBuildDownloadLocally(latest_build):
    status = localFile.pathControl(latest_build)

    '''
    0 - Go ahead and download
    1 - It's already downloaded
    2 - Go ahead to download it and create a Version control since it wasn't created yet
    3 - Fail 
    '''

    if status == 0:
        # Go ahead and download
        return True

    elif status == 1:
        # It's already downloaded
        return False       
    
    elif status == 2:
        # Go ahead and download. Version control wasn't created yet
        return True

    elif status == 3:
        # Fail
        print('Please check if Version_control folder exists')
        return False


def getBuildNameFromDir(build_path):
    # Server pattern: 'Build6.x.x.x_0123456/'
    # After clean it: '6.x.x.x_0123456'
    return path_manager(''.join(''.join(str(build_path).split('Build')).split('/'))) 

def startDownloadProcess(client, build_name):
    sftp = client.open_sftp()
    build_path = PATH_MW_528 / build_name / STB_MODEL_MW_528 # /nfs/OpentvOS/v5.2.8/NET/build_name/dgci362_unified_glibc_bc/
    print('Path:', build_path.as_posix())
    build_name_clean = getBuildNameFromDir(build_name) # Take build name without unnecessary words to persist on Build Number Control (txt)
    
    try:

        ### Handling MW 528 ###

        #Get all Build_Production_XPTO folders (without attributes) from sftp (MW 5.2.8 only)
        path_product_folder = []
        for folders in sftp.listdir_attr(build_path.as_posix()):
            if not(folders.filename == PRODUCT_TO_NOT_DOWNLOAD_MW_528):
                path_product_folder.append(folders.filename)

        new_local_path = path_manager(localFolder.createSTBModelFolder(path_manager(localFolder.createBuildNameFolder(build_name_clean)), STB_MODEL_MW_528)) # STB Model folder
                
        # Loop to create all Build_Production_XPTO 
        for folder in path_product_folder:
            localFolder.createBuildTypeFolder(new_local_path, folder)

        # Create local sub-folders from Build_Production_XPTO
        # /nfs/OpentvOS/v5.2.8/NET/build_name/STB_Model/build_production_XPTO
        for folder in path_product_folder:
            return createLocalDirectories(sftp, path_manager.joinpath(build_path, path_manager(folder)).as_posix(), path_manager.joinpath(new_local_path, folder))

    except (EnvironmentError, IOError, OSError) as e:
        print(e)

def createLocalDirectories(sftp, remote_dir, local_path):
    current_path = []
    remote_path = []
    
    for dir in sftp.listdir_attr(remote_dir):
        if dir.filename not in FOLDERS_TO_NOT_DOWNLOAD: 
            current_path.append(path_manager(localFolder.createLocalFolders(local_path, dir.filename)))
            remote_path.append(path_manager.joinpath(path_manager(remote_dir), dir.filename))

    return downloadFiles(sftp, current_path, remote_path)
    
def downloadFiles(sftp, current_path, remote_path):
    file_name_for_progress_bar = "" # Not necessary, just a good view to progress bar
    callback_progressbar, progressbar = progressBarView(ascii=False, desc=file_name_for_progress_bar, unit='k', unit_scale=True)
    i = 0
    for remote_dir in remote_path:
        for remote_file in sftp.listdir_attr(remote_dir.as_posix()):
            
            file_name_for_progress_bar = remote_file.filename            
            if remote_file.filename not in FILES_TO_NOT_DOWNLOAD:
                print(file_name_for_progress_bar)
                sftp.get(path_manager.joinpath(remote_dir, remote_file.filename).as_posix(), path_manager.joinpath(current_path[i], remote_file.filename), callback_progressbar)      
        i += 1
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


if __name__ == '__main__':
    client = connectionToServer()
    if (client == False):
        print('Finishing script...')
        
    else:
        latestBuild = getLatestBuildNameFromServer(client)
        print('Latest Build from Server:', latestBuild)
        status = getLatestBuildDownloadLocally(str(latestBuild.name))
        
        if(status == True):
            startDownloadProcess(client, latestBuild)  
        
        elif(status == False):
            print('Finishing script...')
        
        else:
            print('Finishing script...')
    client.close()