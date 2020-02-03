
from pathlib import Path as path_manager
import sys
import logging

debug = True # Used to avoid Traceback errors when Fails

PATH_FOLDER = path_manager(r"Z:\01.Opentv5\16.Version_control")
FILE_NAME = "version_control.txt"
PATH_COMPLETE = PATH_FOLDER / FILE_NAME 
#OLDER_BUILD = "6.1.2.55"
#LATEST_BUILD = "Build6.1.2.7_1166816" 

##### Log environment #################################################################
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logs/file_manager.log')
formatter = logging.Formatter('%(asctime)s: %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)
#######################################################################################

'''
0 - Go ahead and download
1 - It's already downloaded
2 - Go ahead and download. Version control wasn't created yet
3 - Fail 
'''

def pathControl(LATEST_BUILD):
    if PATH_FOLDER.exists() and PATH_COMPLETE.exists():
        try:
            print('Checking latest build downloaded')
            log.info('Checking latest build downloaded')
            return checkLatestBuildDownloaded(LATEST_BUILD)                  
                
        except (EnvironmentError, IOError, OSError) as e:
            log.exception('An error occured on Path Control function')
            return e
            
    elif not(PATH_FOLDER.exists()):
        print('Folder not found:', PATH_FOLDER)
        log.warning(f'Folder not found: {PATH_FOLDER}')
        return 3
    
    else:
        print('File not exist. Creating a new one...')
        createFileControl(LATEST_BUILD)
        log.info('File does not exist. Creating a new one.')
        return 2
        

def checkLatestBuildDownloaded(LATEST_BUILD):
    with PATH_COMPLETE.open() as version_control:
        try:
            OLDER_BUILD = version_control.read()
            if OLDER_BUILD == '':
                print('File is empty. Creating a new one with build name received:',LATEST_BUILD)
                log.warning(f'File is empty. Creating a new one with build name {LATEST_BUILD}')
                createFileControl(LATEST_BUILD)
                return 2
            elif OLDER_BUILD != LATEST_BUILD and OLDER_BUILD != '':
                print(f'Build {LATEST_BUILD} received is different of {OLDER_BUILD} from history.')
                print('Updating latest build from local file...')
                log.info(f'Updating latest build {LATEST_BUILD} from local file')
                createFileControl(LATEST_BUILD)
                return 0
            else:
                print(f'Build {LATEST_BUILD} received is the same of {OLDER_BUILD} from history.')
                print('File not updated.')
                log.info(f'Latest build locally ({OLDER_BUILD}) is the same from remote server ({LATEST_BUILD}).')
                return 1

        except (EnvironmentError, IOError, OSError)  as e:
            print('Not possible to open history file:', e)
            log.exception('An error occured to check the latest build downloaded')
            return e

def createFileControl(LATEST_BUILD):
    with PATH_COMPLETE.open('w') as version_control:
        try:
            version_control.write(str(LATEST_BUILD))
            print('File updated to:', LATEST_BUILD)
            log.info(f'File updated to {LATEST_BUILD}')
            return str(LATEST_BUILD)
        except (EnvironmentError, IOError, OSError)  as e:
            print('Not possible to open history file:', e)
            log.exception('An error occured to create file control')
            return e    

# Function to not print traceback unless debug is True
def exceptionHandler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if debug:
        print('\n*** Error ***')
        # Display all exceptions catched using debug_hook
        debug_hook(exception_type, exception, traceback)
    else:
        print(f'\t{exception_type.__name__}: {exception}')# Exception.name: exception
sys.excepthook = exceptionHandler    
