from pathlib import Path as path_manager
import sys
import logging

debug = True # Used to avoid Traceback errors when Fails

MW_DICT = {
    'NET_R6': path_manager(r'Z:\01.Opentv5\00.Versions\NET\Release6.1'),
    'NET_R4': path_manager(r'Z:\01.Opentv5\00.Versions\NET\Release4.1'),
    'NET_R2': path_manager(r'Z:\01.Opentv5\00.Versions\NET\Release2.5')
}

##### Log environment ###############################################################################################################################################
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logs/folder_managerOS.log')
formatter = logging.Formatter('%(asctime)s: %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)
#####################################################################################################################################################################

def createBuildNameFolder(build_name, MW_VERSION):
    LOCAL_PATH = MW_DICT.get(MW_VERSION)
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

def createLocalFolders(new_path, folder_name):
    try:
        path_manager.mkdir(new_path / folder_name)
        log.info(f'Creating local folder {folder_name}')
        return new_path / folder_name
    
    except (EnvironmentError, IOError, OSError) as e:
        log.exception('An error occured to create local folders')
        print(e)
    
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
        'ENGG',
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
 
def createSubDirectories(model_folder, local_path):
    #sub_folders_513_dict = {}
    model = ngCleanModelName(model_folder)
    if not(path_manager.joinpath(local_path, model[0]).exists()):
        
        createLocalFolders(local_path, path_manager.joinpath(local_path, model[0]))
        if not(path_manager.joinpath(local_path, model[0], model[1]).exists()):
            #sub_folders_513_dict[''.join(model)] = path_manager(createLocalFolders(path_manager.joinpath(local_path, model[0]), model[1]))
            path = path_manager(createLocalFolders(path_manager.joinpath(local_path, model[0]), model[1]))

    elif not(path_manager.joinpath(local_path, model[0], model[1]).exists()):
        path = path_manager(createLocalFolders(path_manager.joinpath(local_path, model[0]), model[1]))
    
    return path
  
# Function to not print traceback unless debug is True
def exceptionHandler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if debug:
        print('\n*** Error ***')
        # Display all exceptions catched using debug_hook
        debug_hook(exception_type, exception, traceback)
    else:
        print(f'\t{exception_type.__name__}: {exception}')# Exception.name: exception
sys.excepthook = exceptionHandler

