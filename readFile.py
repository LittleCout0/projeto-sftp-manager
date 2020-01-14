#!-*- conding: utf8 -*-
from os import path
#import sftp_connection as sftp
import glob

PATH_FOLDER = "ftp_test/"
FILE_NAME = "test.txt"
PATH_COMPLETE = PATH_FOLDER+FILE_NAME
OLDER_BUILD = "build6.1.2.6"
LATEST_BUILD = "build6.1.2.7" # deverá ser inicializado no __init__


def checkLatestBuildDownloaded():
    with open(PATH_COMPLETE,"r") as arq:
        OLDER_BUILD = arq.read()
        print("Última build baixada: "+OLDER_BUILD)

def createFileControl(LATEST_BUILD):
    with open(PATH_COMPLETE, "w") as arq:
        arq.write(LATEST_BUILD)
        print('Arquivo criado com a versão da última build baixada:', LATEST_BUILD)

#def checkLatestBuildFromServer():
    #chama sftp file

if __name__ == '__main__':
    #checkLatestBuildFromServer() 
    if (path.exists(PATH_FOLDER)):
        try:
            if(path.exists(PATH_COMPLETE)):
                # Cenário que vai verificar qual foi a última build baixada
                checkLatestBuildDownloaded()

                # Cenário que vai verificar se o último arquivo baixado é também o último disponível no server
                    
            elif not(path.exists(PATH_COMPLETE)):
                createFileControl(LATEST_BUILD)
                # Cenário que vai criar o arquivo caso não exista e adicionar a build que foi baixada
                
        except OSError as osError:
            print('Erro ao acessar o arquivo:', osError)
            print('Encerrando o script')
    else:
        print('Pasta '+PATH_FOLDER+' não encontrada.')
        print('Encerrando o script')
