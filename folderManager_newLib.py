from pathlib import Path as path_manager
import sys
import logging

debug = True # Used to avoid Traceback errors when Fails

#caminho até as Builds: \\10.4.164.16\\sao\\01.Opentv5\\00.Versions\\NET\\6.1Release
#path_sub_folder_release = ['release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_noOTA','release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_OTA','release_netbrazil_4tnfx_uhd_hdcp_nasc_production_OTA']
#path_sub_folder_dev = ['dev_netbrazil_4tnfx_uhd_hdcp_nasc_integration_noOTA','dev_netbrazil_4tnfx_uhd_hdcp_nasc_integration_OTA','dev_netbrazil_4tnfx_uhd_hdcp_nasc_production_OTA']
#folders_name = ['build_product_release','build_product_sdk','build_product_DEV'] #variavel que virá do sftp
#sub_folder_name = ['release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_noOTA','release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_OTA','release_netbrazil_4tnfx_uhd_hdcp_nasc_production_OTA']#variavel que virá do sftp
#build_name = '6.1.2.10'
LOCAL_PATH = path_manager(r'C:\Users\wsouza\Desktop\SFTP Project')

def createBuildNameFolder(build_name):
    if(LOCAL_PATH.exists()):
        try:
            print(f'Creating {build_name} folder')
            path_manager.mkdir(path_manager.joinpath(LOCAL_PATH, build_name))
            return LOCAL_PATH / build_name
        
        except (EnvironmentError, IOError, OSError) as e:
            print(e)
    
    elif not(LOCAL_PATH.exists()):
        print('Path not found.')

def createSTBModelFolder(new_path, stb_model):
    try:
        print(f'Creating {stb_model} folder')
        path_manager.mkdir(new_path / stb_model)
        return new_path / stb_model
    
    except (EnvironmentError, IOError, OSError) as e:
        print(e)

def createBuildTypeFolder(new_path, mw_type):
    try:
        print(f'Creating {mw_type} folder')
        path_manager.mkdir(new_path / mw_type)
        return new_path / mw_type
    
    except (EnvironmentError, IOError, OSError) as e:
        print(e)
        
def createLocalFolders(new_path,folder_name):
    try:
        path_manager.mkdir(new_path / folder_name)
        return new_path / folder_name
    
    except (EnvironmentError, IOError, OSError) as e:
        print(e)


def createLocalSubFolders(new_path, sub_folder_name):
    try:
        path_manager.mkdir(new_path / sub_folder_name)
        return new_path / sub_folder_name
    
    except (EnvironmentError, IOError, OSError) as e:
        print(e)
  
# Function to not print traceback unless debug is True
def exceptionHandler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if debug:
        print('\n*** Error ***')
        # Display all exceptions catched using debug_hook
        debug_hook(exception_type, exception, traceback)
    else:
        print(f'\t{exception_type.__name__}: {exception}')# Exception.name: exception
sys.excepthook = exceptionHandler

### Test ### 
'''
new_local_path = LOCAL_PATH / createBuildNameFolder(build_name)
path_sub_folder = path_sub_folder_release
path_product_folder = folders_name
for sdk in path_product_folder:
    if 'build_product_sdk' == sdk:
        path_product_folder.remove(sdk)
        
for folder_name in path_product_folder:
    try:
        #wa_new_path = new_local_path #WorkAround!
        new_local_path = new_local_path / createLocalFolders(new_local_path, folder_name)
        for sub_folder_name in path_sub_folder:
            createLocalSubFolders(new_local_path, sub_folder_name)  
        new_local_path = new_local_path.parents[0]
        path_sub_folder = path_sub_folder_dev 
    except (EnvironmentError, IOError, OSError) as e:
        print(e)'''