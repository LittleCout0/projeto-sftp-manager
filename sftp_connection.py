# -*- coding: utf-8 -*-
from paramiko import SSHClient, AutoAddPolicy
import pysftp
import os
import time
import glob


HOST = 'zrhftp.hq.k.grp'
USER = 'wsouza'
PWORD = 'Willi@m.06'
PORT = 22

PATH_MW_528 = '/nfs/OpentvOS/v5.2.8/NET/'
BUILD_MW_528 = 'Build6.1.2.6_1164573/'#variável que virá do txt
STB_MODEL_MW_528 = 'dgci362_unified_glibc_bc/'
FLAVOR_TYPE_MW_528 = 'build_product_release/'
FLAVOR_SUBTYPE_MW_528 = 'release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_noOTA/'
LATEST_BUILD_MODIFIED = ''#variável necessária para saber se já baixamos ou não
PATH_COMPLETE = PATH_MW_528 + BUILD_MW_528 + STB_MODEL_MW_528 + FLAVOR_TYPE_MW_528 + FLAVOR_SUBTYPE_MW_528
print('Arquivos em:', PATH_COMPLETE)

def connectionToServer():
    with SSHClient() as client:
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(HOST, PORT, username=USER, password=PWORD)
        print('Conexão estabelecida com', HOST)
        #Possivelmente tenha que chamar de novo a conexão visto que toda vez que usamos "WITH" 
        # Ele cuida de fechar as conexões após rodar o bloco de código

def listDirectory():
    with SSHClient() as client:
        try:
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(HOST, PORT, username=USER, password=PWORD)
            print('Conexão Estabelecida com', HOST)

            with client.open_sftp() as sftp:     
                try:   
                    dir_MW_528 = sftp.listdir_attr(PATH_MW_528)
                    latest = 0
                    latestfile = None
                    print('Filtrando último arquivo modificado em:', PATH_MW_528)
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
        except (Exception) as e:
            print(e)
        

def getBuildNameFromDir(build_path):
    # Elimina o PATH e mantém somente o Build_name
    build_name = ''.join(''.join(build_path.split('Build')).split('/')) 
    return build_name


if __name__ == '__main__':
    connectionToServer()
    LATEST_BUILD_MODIFIED = getBuildNameFromDir(listDirectory())
    print(LATEST_BUILD_MODIFIED)

