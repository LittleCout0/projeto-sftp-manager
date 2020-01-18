# -*- coding: utf-8 -*-
from paramiko import SSHClient, AutoAddPolicy
import fileManager as localFile
import pysftp
import os
import time

HOST = '10.176.226.172'#'zrhftp.hq.k.grp'
USER = 'wsouza'
PWORD = 'Willi@m.06'
PORT = 22

PATH_MW_528 = '/nfs/OpentvOS/v5.2.8/NET/'
BUILD_MW_528 = ''
STB_MODEL_MW_528 = 'dgci362_unified_glibc_bc/'
FLAVOR_TYPE_MW_528 = 'build_product_release/'
FLAVOR_SUBTYPE_MW_528 = 'release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_noOTA/'
LATEST_BUILD_MODIFIED = ''#variável necessária para saber se já baixamos ou não
PATH_COMPLETE = PATH_MW_528 + BUILD_MW_528 + STB_MODEL_MW_528 + FLAVOR_TYPE_MW_528 + FLAVOR_SUBTYPE_MW_528
print('Arquivos em:', PATH_COMPLETE)

'''def listDirectory(client):
        sftp = client.open_sftp()
        try:   
            dir_MW_528 = sftp.listdir_attr(PATH_MW_528)
            latest = 0
            latestfile = None
            print('Getting latest file in:', PATH_MW_528)
            for file_attribute in dir_MW_528:
                if file_attribute.st_mtime > latest:
                    latest = file_attribute.st_mtime
                    latestfile = file_attribute.filename
            
            print('Latest:', latest)
            print('LatestFile:',latestfile)
            #p='/nfs/OpentvOS/v5.2.8/NET/Build6.1.1.7_1155080/dgci362_unified_glibc_bc/build_product_release/release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_noOTA/'
            #print('Baixando arquivo: '+'sysinit.ramdisk.txt')
            #sysinit.ramdisk.txt
            #sftp.get(p+'sysinit.ramdisk.txt', 'C:\\Users\\wsouza\\Downloads\\test\\sysinit.ramdisk.txt')
            #print('Salvo em: '+'C:\\Users\\wsouza\\Downloads\\test\\')
            #https://github.com/tqdm/tqdm#description-and-additional-stats
        except (Exception) as e:
            print(e)
            client.close()'''

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
        #Possivelmente tenha que chamar de novo a conexão visto que toda vez que usamos "WITH" 
        # Ele cuida de fechar as conexões após rodar o bloco de código
            
def getLatestBuildNameFromServer(client):
    sftp = client.open_sftp()
    try:   
        dir_MW_528 = sftp.listdir_attr(PATH_MW_528)
        latest = 0
        latest_folder = None
        #print('Filtrando último arquivo modificado em:', PATH_MW_528)
        for folder_attribute in dir_MW_528:
            if folder_attribute.st_mtime > latest:
                #latest = folder_attribute.st_mtime
                latest_folder = folder_attribute.filename
        return latest_folder
    except (Exception) as e:
        print(e)

def getLatestBuildDownloadLocally(latest_build):
    if(localFile.pathControl(latest_build)) == 0:
        print('Please check local path')
    elif(localFile.pathControl((latest_build)) == False):
        #First create directories locally
        #then start Download
    elif(localFile.pathControl((latest_build)) == True):
        print('Build local is the same of latest from server')        

def getBuildNameFromDir(build_path):
    # Elimina o PATH e mantém somente o Build_name
    build_name = ''.join(''.join(build_path.split('Build')).split('/')) 
    return build_name

def downloadLatestBuild(client, build_name):
    sftp = client.open_sftp()
    build_path = PATH_MW_528+build_name+STB_MODEL_MW_528
    build_name_clean = getBuildNameFromDir(build_name)
    try:
        #usar lista diretorios aqui
        #faremos somente release e dev
        #limpar nome ou pegar final da string e confirmar para não baixar sdk
        #para cada iteração criamos um diretório local
        #e chamamos a funcão de download

if __name__ == '__main__':
    connectionToServer()
    LATEST_BUILD_MODIFIED = getBuildNameFromDir(listDirectory())
    print(LATEST_BUILD_MODIFIED)

