# -*- coding: utf-8 -*-
# trabalhar com PATHLIB para evitar atualizações do python quebre o código
import os
import pathlib


'''caminho até as Builds: \\10.4.164.16\\sao\\01.Opentv5\\00.Versions\\NET\\6.1'''
path_sub_folder_release = ['release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_noOTA/','release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_OTA/','release_netbrazil_4tnfx_uhd_hdcp_nasc_production_OTA/']
path_sub_folder_dev = ['dev_netbrazil_4tnfx_uhd_hdcp_nasc_integration_noOTA/','dev_netbrazil_4tnfx_uhd_hdcp_nasc_integration_OTA/','dev_netbrazil_4tnfx_uhd_hdcp_nasc_production_OTA/']
folders_name = ['build_product_release/','build_product_sdk/','build_product_DEV/'] #variavel que virá do sftp
sub_folder_name = ['release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_noOTA/','release_netbrazil_4tnfx_uhd_hdcp_nasc_integration_OTA/','release_netbrazil_4tnfx_uhd_hdcp_nasc_production_OTA/']#variavel que virá do sftp
PATH = r'C:/Users/William/Desktop/SFTP Project/' 

def createBuildNameFolder(build_name):
    if(os.path.exists(PATH)):
        print('Creating %s folder' % build_name)
        os.mkdir(PATH+build_name)
        return os.path.join(PATH, build_name)
    
    elif not(os.path.exists(PATH)):
        print('Path not found.')
        
def createLocalFolders(new_path,folder_name):
    try:
        os.mkdir(new_path+folder_name)
        return os.path.join(new_path, folder_name)
    except OSError as e:
        print(e)
      
    
def createLocalSubFolders(new_path, sub_folder_name):
    try:
        os.mkdir(new_path+sub_folder_name)    
    except OSError as e:
        print(e)
 
new_path = os.path.join(PATH, createBuildNameFolder('local/'))
path_sub_folder = path_sub_folder_release
path_product_folder = folders_name
for sdk in path_product_folder:
    if 'build_product_sdk/' == sdk:
        path_product_folder.remove(sdk)
        
for folder_name in path_product_folder:
    try:
        wa_new_path = new_path #WorkAround!
        new_path = os.path.join(new_path, createLocalFolders(new_path, folder_name))
        for sub_folder_name in path_sub_folder:
            createLocalSubFolders(new_path,sub_folder_name)          
        path_sub_folder = path_sub_folder_dev
        new_path = wa_new_path
    except Exception as e:
        print(e)
    
'''
def makeDir_old(list_dir_name):       
    if os.path.exists(PATH):
        #new_path_folder = PATH
        try:
            print('Creating %d folders' % len(list_dir_name))
            for folder_name in list_dir_name: #list_dir_name.filename:
                #os.mkdir(new_path_folder.join(folder_name.filename))
                print(folder_name)
                os.mkdir(PATH+folder_name)
                SUB_DIR_NAMES = os.path.join(PATH, folder_name)
                #new_path_folder = os.path.join(new_path_folder, folder_name.filename)
                #'sub_path_folder = os.path.join(new_path_folder, folder_name)
                #for sub_folder_name in list_sub_dir_name: #list_sub_dir_name.filename:
                    #os.mkdir(new_path_folder.join(sub_folder_name.filename))
                #    print(list_sub_dir_name)
                #    os.mkdir(sub_path_folder+sub_folder_name)'            
        except Exception as e:
            print(e)
    elif not(path.exists(PATH)):
        print('Path not found.')

def makeSubDir_old(list_sub_dir_name):
    try:
        #sub_path_folder = os.path.join(new_path_folder, folder_name)
        for sub_folder_name in SUB_DIR_NAMES: #list_sub_dir_name.filename:
            #os.mkdir(new_path_folder.join(sub_folder_name.filename))
            print(list_sub_dir_name)
            os.mkdir(SUB_DIR_NAMES+sub_folder_name)    
    except Exception as e:
        print(e)'''