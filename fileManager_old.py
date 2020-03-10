#!-*- conding: utf8 -*-
from os import path

PATH_FOLDER = "ftp_test/"
FILE_NAME = "test.txt"
PATH_COMPLETE = PATH_FOLDER+FILE_NAME
#OLDER_BUILD = "build6.1.2.6"
LATEST_BUILD = "build6.1.1.6" # deverá ser inicializado no __init__

def pathControl(LATEST_BUILD):
    if path.exists(PATH_FOLDER) and path.exists(PATH_COMPLETE):
        try:
            print('Checking latest build downloaded')
            return checkLatestBuildDownloaded(LATEST_BUILD)                  
                
        except OSError as osError:
            return osError
            
    elif not(path.exists(PATH_FOLDER)):
        print('Path not found:',PATH_FOLDER)
        return 0
            #return createFileControl(LATEST_BUILD)
            # Cenário que vai criar o arquivo caso não exista e adicionar a build que foi baixada
    else:
        print('File not exists. Creating a new one...')
        return createFileControl(LATEST_BUILD)
        

def checkLatestBuildDownloaded(LATEST_BUILD):
    with open(PATH_COMPLETE,"r") as arq:
        try:
            OLDER_BUILD = arq.read()
            if OLDER_BUILD == '':
                print('File is empty. Creating a new one with build name received:',LATEST_BUILD)
                createFileControl(LATEST_BUILD)
                return False
            elif OLDER_BUILD != LATEST_BUILD and OLDER_BUILD != '':
                print('Build '+LATEST_BUILD+' received is different of '+OLDER_BUILD+' from history.')
                print('Updating latest build from local file...')
                createFileControl(LATEST_BUILD)
                return False
            else:
                print('Build '+LATEST_BUILD+' received is the same of '+OLDER_BUILD+' from history.')
                print('File not updated.')
                return True
        except OSError as osError:
            print('Not possible to open history file:',osError)
            return osError

def createFileControl(LATEST_BUILD):
    with open(PATH_COMPLETE, "w") as arq:
        try:
            arq.write(LATEST_BUILD)
            print('File updated to:',LATEST_BUILD)
            return LATEST_BUILD
        except OSError as osError:
            print('Not possible to open history file:',osError)
            return osError        
    
print(pathControl(LATEST_BUILD))