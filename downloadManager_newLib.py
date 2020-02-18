from paramiko import SSHClient, AutoAddPolicy
import fileManager_newLib as localFile
import folderManager_newLib as localFolder
from pathlib import Path as path_manager
from tqdm import tqdm
import logging

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

FOLDERS_TO_NOT_DOWNLOAD = [
    'release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_OTA',
    'release_netbrazil_4tnfx_uhd_hdcp_nasc_production_noOTA',
    'dev_netbrazil_4tnfx_hd_nohdcp_nonasc_integration_alpha', 
    'release_netbrazil_2tnfx_hd_hdcp_nasc_integration_OTA',
    'dev_netbrazil_2tnfx_hd_nohdcp_nonasc_integration'
]

FILES_TO_NOT_DOWNLOAD = [
    'CAROUSEL-net-dgci362_otv5_loader_kernel_squashfs_FWver-0x6127_PID-0x1D76_usageID-0x01to0x0A.ts',
    'rootfs.squashfs',
    'otv5_loader_kernel_squashfs.bin',
    'DGCI362_IMAGE', 
    'ubifs-128k-2048-7260a0.img',
    'rootfs.tar.bz2',
    'zImageDTB',
    'zImage',
    'ubifs-128k-2048-7429b0.img',
    'vmlinuz-main',
    'dci738net_usbpayload',
    'kernel_dci738net.ssv',
    'kernel_dci738net.ssv.tmm',
    'vmlinux.bin'
]


#####################################################################################################################################################################

def getBuildNameFromDir(build_path):
    # Server pattern: 'Build6.x.x.x_0123456/'
    # After clean it: '6.x.x.x_0123456'
    return path_manager(''.join(''.join(str(build_path).split('Build')).split('/')))

def startPathCreator(client, PATH_MW, STB_MODEL, local_build_folder):

    sftp = client.open_sftp()
    if(STB_MODEL):
        build_path = PATH_MW / STB_MODEL # /nfs/OpentvOS/v5.x.x/NET/Build6.x.x.x/brand/
        
    elif not(STB_MODEL):
        build_path = PATH_MW
        
    print('Path:', build_path.as_posix())
    log.info(f'Path created to start download process: {build_path} ')
    #build_name_clean = getBuildNameFromDir(build_name) # Take build name without unnecessary words to persist on Build Number Control (txt)

    try:
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
            createLocalSubDirectories(sftp, path_manager.joinpath(build_path, path_manager(folder)).as_posix(), path_manager.joinpath(new_local_path, folder))

    except (EnvironmentError, IOError, OSError) as e:
        print(e)
        log.exception('An error occured to start download process')

def createLocalSubDirectories(sftp, remote_dir, local_path):
    current_path = []
    remote_path = []
    
    for dir in sftp.listdir_attr(remote_dir):
        if dir.filename not in FOLDERS_TO_NOT_DOWNLOAD: 
            current_path.append(path_manager(localFolder.createLocalFolders(local_path, dir.filename)))
            remote_path.append(path_manager.joinpath(path_manager(remote_dir), dir.filename))

    return downloadFiles(sftp, current_path, remote_path)
    
def downloadFiles(sftp, current_path, remote_path):
    file_name_for_progress_bar = "" # Not necessary, just a improve to progress bar
    callback_progressbar, progressbar = progressBarView(ascii=False, desc=file_name_for_progress_bar, unit='b', unit_scale=True)
    i = 0 # To control the current_path folders list
    
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

        PATH_MW = path_manager.joinpath(PATH_ROOT, MW_VERSION, NET, latestBuild_path) #/nfs/OpentvOS/v5.2.8/NET/Build6.x.x.x
        startPathCreator(client, PATH_MW, STB_MODEL, local_build_folder)