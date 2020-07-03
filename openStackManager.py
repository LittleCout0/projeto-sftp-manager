from pathlib import Path as path_manager
import urllib.request
from tqdm import tqdm
import fileManagerOS as localFile
import folderManagerOS as localFolder
import win32com.client
import re
import logging
import time
from functools import wraps

debug = False  # Used to avoid Traceback errors when Fails

url_pattern = '((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|)|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com)\b/?(?!@)))'

# Log environment
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logs/openStackManager.log')
formatter = logging.Formatter('%(asctime)s: %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)
########################################################################################################################################################

########################################################################################################################################################
MW_VERSION_513 = 'NET_R2'
MW_VERSION_524 = 'NET_R4'
MW_VERSION_528 = 'NET_R6'
MW_VERSION_LIST = [MW_VERSION_528, MW_VERSION_524, MW_VERSION_513]

HUMAX_MODEL = 'humax7430_uclibc_bc'
PACE_MODEL = 'pace7430_uclibc_bc'
TECH_MODEL = 'tc7430_uclibc_bc'


########################################################################################################################################################


def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """
    Wiki: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    
    def deco_retry(f):
        
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = ("%s, Retrying in %d seconds..." % (str(e), mdelay))
                    if logger:
                        log.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        
        return f_retry  # true decorator
    
    return deco_retry


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


@retry(Exception, tries=2)
def download_url(url, output_path):
    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)


def getBuildEmail(indice):
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")  # Outlook access
        inbox = outlook.GetDefaultFolder(6).Folders('JIRAs').Folders('Build Request').Folders('Builds to Download')
        messages = inbox.Items
        messages.Sort("[ReceivedTime]", True)
        
        subject_content = messages[indice].subject
        body_content = messages[indice].body
        return subject_content, body_content
    
    except Exception as e:
        print(e)
        log.error(f'Error to get build from email: {e}')


def getLatestBuildDownloadLocally(latest_build, MW_VERSION):
    status = localFile.pathControl(latest_build, MW_VERSION)
    
    '''
    0 - Go ahead and download
    1 - It's already downloaded
    2 - Go ahead to download it and create a Version control since it wasn't created yet
    3 - Fail
    '''
    
    if status == 0:
        # Go ahead and download
        log.info('Status == 0. Go ahead and download')
        return True
    
    elif status == 1:
        # It's already downloaded
        log.info('Status == 1. It is already downloaded')
        return False
    
    elif status == 2:
        # Go ahead and download. Version control wasn't created yet
        log.info(
            'Status == 2. Go ahead and download. Version control was not created yet')
        return True
    
    elif status == 3:
        # Fail
        print('Please check if Version_control folder exists')
        log.error('Status == 3. Fail (Version_control folder exist?).')
        return False


if __name__ == '__main__':
    
    # Look for the latest three emails on folder
    indice = 0
    while indice != 3:
        subject_content, body_content = getBuildEmail(indice)
        build_name = ''.join(re.findall('((?:NET_R)|(?:[0-9])|(?:[.]))', subject_content))
        print(f'Checking if {build_name} was already downloaded...')
        MW = build_name.split('.')
        
        if MW[0] == MW_VERSION_528:
            build_name = ''.join(build_name.split('NET_R'))
            status = getLatestBuildDownloadLocally(build_name, MW_VERSION_528)
            local_build_folder = localFolder.createBuildNameFolder(build_name, MW_VERSION_528)
            urls = set(re.findall(url_pattern, body_content))
            
            for url in urls:
                if not ('jira.opentv.com' in url.split('/')):
                    print(f'Sagem 4K: {url}')
                    log.info(f'Downloading build: {url}')
                    try:
                        download_url(url, path_manager.joinpath(local_build_folder, url.split('/')[-1]))
                    except urllib.error.ContentTooShortError:
                        pass
            
            localFile.createFileControl(build_name, MW_VERSION_524)
            print('Control file created')
        
        elif MW[0] == MW_VERSION_524:
            build_name = ''.join(build_name.split('NET_R'))
            print(build_name)
            status = getLatestBuildDownloadLocally(build_name, MW_VERSION_524)
            local_build_folder = localFolder.createBuildNameFolder(build_name, MW_VERSION_524)
            urls = set(re.findall(url_pattern, body_content))
            
            for url in urls:
                if not ('jira.opentv.com' in url.split('/')):
                    print(f'Sagem 4K: {url}')
                    try:
                        log.info(f'Downloading build: {url}')
                        download_url(url, path_manager.joinpath(local_build_folder, url.split('/')[-1]))
                    
                    except urllib.error.ContentTooShortError:
                        pass
            localFile.createFileControl(build_name, MW_VERSION_524)
            print('Control file created')
        
        elif MW[0] == MW_VERSION_513:
            build_name = ''.join(build_name.split('NET_R'))
            status = getLatestBuildDownloadLocally(build_name, MW_VERSION_513)
            local_build_folder = localFolder.createBuildNameFolder(build_name, MW_VERSION_513)
            urls = set(re.findall(url_pattern, body_content))
            
            sub_folders_513_dict = {}
            
            sub_folders_513_dict['HUMAX_2T'] = localFolder.createSubDirectories(HUMAX_MODEL + '_2T', local_build_folder)
            sub_folders_513_dict['HUMAX_3P'] = localFolder.createSubDirectories(HUMAX_MODEL + '_3P', local_build_folder)
            sub_folders_513_dict['PACE_2T'] = localFolder.createSubDirectories(PACE_MODEL + '_2T', local_build_folder)
            sub_folders_513_dict['PACE_3P'] = localFolder.createSubDirectories(PACE_MODEL + '_3P', local_build_folder)
            sub_folders_513_dict['TECH_2T'] = localFolder.createSubDirectories(TECH_MODEL + '_2T', local_build_folder)
            
            for url in urls:
                if not ('jira.opentv.com' in url.split('/')):
                    if HUMAX_MODEL in url.split('/'):
                        if '2t' in url.split('_'):
                            try:
                                print(f'Humax 2T: {url}')
                                log.info(f'Downloading build: {url}')
                                download_url(url, path_manager.joinpath(sub_folders_513_dict['HUMAX_2T'],
                                                                        url.split('/')[-1]))
                            except urllib.error.ContentTooShortError:
                                pass
                        elif '3p' in url.split('_'):
                            print(f'Humax 3P:{url}')
                            log.info(f'Downloading build: {url}')
                            download_url(url,
                                         path_manager.joinpath(sub_folders_513_dict['HUMAX_3P'], url.split('/')[-1]))
                    elif PACE_MODEL in url.split('/'):
                        if '2t' in url.split('_'):
                            print(f'Pace 2T:{url}')
                            log.info(f'Downloading build: {url}')
                            download_url(url,
                                         path_manager.joinpath(sub_folders_513_dict['PACE_2T'], url.split('/')[-1]))
                        elif '3p' in url.split('_'):
                            print(f'Pace 3P:{url}')
                            log.info(f'Downloading build: {url}')
                            download_url(url,
                                         path_manager.joinpath(sub_folders_513_dict['PACE_3P'], url.split('/')[-1]))
                    elif TECH_MODEL in url.split('/'):
                        if '2t' in url.split('_'):
                            try:
                                print(f'Tech 2T:{url}')
                                log.info(f'Downloading build: {url}')
                                download_url(url,
                                             path_manager.joinpath(sub_folders_513_dict['TECH_2T'], url.split('/')[-1]))
                            except urllib.error.ContentTooShortError:
                                pass
            
            localFile.createFileControl(build_name, MW_VERSION_513)
            print('Control file created')
        
        indice += 1
