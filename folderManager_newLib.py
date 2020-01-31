from pathlib import Path as path_manager
import sys
import logging

debug = True # Used to avoid Traceback errors when Fails

LOCAL_PATH = path_manager(r'Z:\01.Opentv5\00.Versions\NET\Release6.1')
logging.basicConfig(filename='folder_manager.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

def createBuildNameFolder(build_name):
    if(LOCAL_PATH.exists()):
        try:
            print(f'Creating {build_name} folder')
            path_manager.mkdir(path_manager.joinpath(LOCAL_PATH, build_name))
            return LOCAL_PATH / build_name
        
        except (EnvironmentError, IOError, OSError) as e:
            logging.exception('An error occured to create build folder')
            print(e)
    
    elif not(LOCAL_PATH.exists()):
        print('Path not found.')

def createSTBModelFolder(new_path, stb_model):
    try:
        print(f'Creating {stb_model} folder')
        path_manager.mkdir(new_path / stb_model)
        return new_path / stb_model
    
    except (EnvironmentError, IOError, OSError) as e:
        logging.exception('An error occured to create STB model folder')
        print(e)

def createBuildTypeFolder(new_path, mw_type):
    try:
        print(f'Creating {mw_type} folder')
        path_manager.mkdir(new_path / mw_type)
        return new_path / mw_type
    
    except (EnvironmentError, IOError, OSError) as e:
        logging.exception('An error occured to create build type folder')
        print(e)
        
def createLocalFolders(new_path,folder_name):
    try:
        path_manager.mkdir(new_path / folder_name)
        return new_path / folder_name
    
    except (EnvironmentError, IOError, OSError) as e:
        logging.exception('An error occured to create local folders')
        print(e)


def createLocalSubFolders(new_path, sub_folder_name):
    try:
        path_manager.mkdir(new_path / sub_folder_name)
        return new_path / sub_folder_name
    
    except (EnvironmentError, IOError, OSError) as e:
        logging.exception('An error occured to create sub-folders')
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
        #wa_new_path = new_local_path 
        new_local_path = new_local_path / createLocalFolders(new_local_path, folder_name)
        for sub_folder_name in path_sub_folder:
            createLocalSubFolders(new_local_path, sub_folder_name)  
        new_local_path = new_local_path.parents[0]
        path_sub_folder = path_sub_folder_dev 
    except (EnvironmentError, IOError, OSError) as e:
        print(e)'''