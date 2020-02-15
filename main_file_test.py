from downloadManager_newLib import startDownloadProcess as download

ROOT = '/nfs/OpentvOS'
MW_VERSION_513 = 'v5.1.3'
MW_VERSION_524 = 'v5.2.4'
MW_VERSION_528 = 'v5.2.8'
STB_MW_528_LIST = ['dgci362_unified_glibc_bc', 'dci738net_glibc_bc']
STB_MW_513_LIST = ['']
MW_VERSION_LIST = ['v5.2.8', 'v5.2.4','v5.1.3']

for MW in MW_VERSION_LIST:
    if(MW == MW_VERSION_528):
        for model in STB_MW_528_LIST:
            print(f"Model: {model}")
            download(ROOT, MW, model)
    else:
        print('Not implemented yet')
