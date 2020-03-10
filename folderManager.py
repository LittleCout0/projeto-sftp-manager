from pathlib import Path as path_manager
import sys
import logging

debug = False # Used to avoid Traceback errors when Fails

MW_DICT = {
    'v5.2.8': path_manager(r'Z:\01.Opentv5\00.Versions\NET\Release6.1'),
    'v5.2.4': path_manager(r'Z:\01.Opentv5\00.Versions\NET\Release4.1'),
    'v5.1.3': path_manager(r'Z:\01.Opentv5\00.Versions\NET\Release2.5')
}

##### Log environment ###############################################################################################################################################
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logs/folder_manager.log')
formatter = logging.Formatter('%(asctime)s: %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)
#####################################################################################################################################################################

def createBuildNameFolder(build_name, MW_VERSION):
    LOCAL_PATH = MW_DICT.get(MW_VERSION.name)
    if(LOCAL_PATH.exists()):
        try:
            print(f'Creating {build_name} folder')
            path_manager.mkdir(path_manager.joinpath(LOCAL_PATH, build_name))
            log.info(f'Creating {build_name} created')
            return LOCAL_PATH / build_name
            
        except (EnvironmentError, IOError, OSError) as e:
            log.exception('An error occured to create build folder')
            print(e)
    
    elif not(LOCAL_PATH.exists()):
        print('Path not found.')
        log.warning(f'Path not found: {LOCAL_PATH}')

def createSTBModelFolder(new_path, stb_model):
    try:
        print(f'Creating {stb_model} folder')
        path_manager.mkdir(new_path / stb_model)
        log.info(f'Creating {stb_model} folder')
        return new_path / stb_model
    
    except (EnvironmentError, IOError, OSError) as e:
        log.exception('An error occured to create STB model folder')
        print(e)

def createBuildTypeFolder(new_path, mw_type):
    try:
        print(f'Creating {mw_type} folder')
        path_manager.mkdir(new_path / mw_type)
        log.info(f'Creating {mw_type} folder')
        return new_path / mw_type
    
    except (EnvironmentError, IOError, OSError) as e:
        log.exception('An error occured to create build type folder')
        print(e)
        
def createLocalFolders(new_path,folder_name):
    try:
        path_manager.mkdir(new_path / folder_name)
        log.info(f'Creating local folder {folder_name}')
        return new_path / folder_name
    
    except (EnvironmentError, IOError, OSError) as e:
        log.exception('An error occured to create local folders')
        print(e)


def createLocalSubFolders(new_path, sub_folder_name):
    try:
        path_manager.mkdir(new_path / sub_folder_name)
        log.info(f'Creating sub folder {sub_folder_name}')
        return new_path / sub_folder_name
    
    except (EnvironmentError, IOError, OSError) as e:
        log.exception('An error occured to create sub-folders')
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