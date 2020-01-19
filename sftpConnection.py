# -*- coding: utf-8 -*-
from paramiko import SSHClient, AutoAddPolicy
import fileManager as localFile
import folderManager as localFolder
import pysftp
import os
import time

HOST = '10.176.226.172'#'zrhftp.hq.k.grp'
USER = 'wsouza'
PWORD = 'Willi@m.06'
PORT = 22

''' Ideia futura após ter tudo rodando e funcionando
Criar um .py gerenciador que popule as variaveis testes abaixo com o que devemos baixar, assim reutiliza o código
de forma correta. 
'''
#PATH_MW = 'v5.2.8' # var para teste. Usar essa variável para altera o MW que queremos acessar
#PATH_MW_528 = '/nfs/OpentvOS/'+PATH_MW+'/NET/'
#BUILD_MW_528 = '' # var para teste. Usar essa variável para guardar última build alterada na lista 
#STB_MODEL_MW_528 = 'dgci362_unified_glibc_bc/' # var para teste. Usar esta variável para alterar qual Brand usar (Tech ou Sagem))
#FLAVOR_TYPE_MW_528 = 'build_product_release/' #var para teste. Usar esta variável para alterar qual tipo vamos baixar (REL, SDK ou DEV)
#FLAVOR_SUBTYPE_MW_528 = 'release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_noOTA/' #var para teste. Usar esta variável para alterar qual sub pasta vamos baixar
LATEST_BUILD_MODIFIED = ''#variável necessária para saber se já baixamos ou não
# PATH_COMPLETE = PATH_MW_528 + BUILD_MW_528 + STB_MODEL_MW_528 + FLAVOR_TYPE_MW_528 + FLAVOR_SUBTYPE_MW_528
#print('Arquivos em:', PATH_COMPLETE)

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
        return True
    elif(localFile.pathControl((latest_build)) == True):
        return False       

def getBuildNameFromDir(build_path):
    # Elimina o PATH e mantém somente o Build_name
    build_name = ''.join(''.join(build_path.split('Build')).split('/')) 
    return build_name

def downloadLatestBuild(client, build_name):
    sftp = client.open_sftp()
    build_path = PATH_MW_528+build_name+STB_MODEL_MW_528
    build_name_clean = getBuildNameFromDir(build_name)
    try:
        '''
        #usar lista diretorios aqui
        #faremos somente release e dev
        #limpar nome ou pegar final da string e confirmar para não baixar sdk
        #para cada iteração criamos um diretório local
        #e chamamos a funcão de download
        1 - primeiro pegamos os tres principais Diretorios (folders_name): 'build_product_release/','build_product_sdk/','build_product_DEV/'
        2 - Limpamos da lista o SDK e salva essa variável: path_product_folder
            path_product_folder = folders_name
            for sdk in path_product_folder.filename:
                if 'build_product_sdk/' == sdk:
                path_product_folder.remove(sdk)
        3 - Separamos as listas por diretorio:
            Pega lista de sub pastas do Release e salva em path_sub_folder_release
            Pega lista de sub pastas do DEV e salva em path_sub_folder_dev
        4 - Fazemos dois FORs para percorrer a lista de diretorios e para cada dir, criamos as sub pastas com o path_sub_dir
        5 - Feito isso trabalhamos com os downloads
        6 - Usamos novamente o percorrer listas, mas já baixamos com o novo PATH que temos:
        
        talvez aqui devemos montar o caminho
         for directory in path_product_dir:
            dirManager.makeDir(directory)
            for sub_directory in path_sub_dir
             dirManager.makeSubDir(sub_directory)             
             sftp.get(path_product_dir+path_sub_dir, path_sub_dir)
            path_sub_dir = path_sub_dir_dev
            
        new_path = os.path.join(PATH, localFolder.createBuildNameFolder(build_name_clean+'/'))
        path_sub_folder = path_sub_folder_release
        path_product_folder = folders_name
        
        for folder_name in path_product_folder:
            try:
                wa_new_path = new_path #WorkAround!
                new_path = os.path.join(new_path, createLocalFolders(new_path, folder_name))
                for sub_folder_name in path_sub_folder:
                    createLocalSubFolders(new_path,sub_folder_name)
                    for files in sftp.listdir_attr(path_sub_folder):
                        sftp.get(path_product_folder+path_sub_folder, path_product_folder+path_sub_folder+files)
                        # rodar com tqdm callback        
                    path_sub_folder = path_sub_folder_dev
                new_path = wa_new_path
            except Exception as e:
                print(e)'''
    

if __name__ == '__main__':
    client = connectionToServer()
    latestBuild = getLatestBuildNameFromServer(client)
    print('Latest Build from Server:', latestBuild)
    if (getLatestBuildDownloadLocally(latestBuild) == False):
        client.close()
    elif(getLatestBuildDownloadLocally(latestBuild == True)):
        downloadLatestBuild(client, latestBuild)

