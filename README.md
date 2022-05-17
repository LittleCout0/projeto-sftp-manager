# SFTP Download Manager
SFTP manager that download latest files from Zurich Server
##
### Tasks handled 
- It handle all MW paths and files at Zurich server: MW528 (4kv2, 4kv1 and dci738), MW524 (4Kv1) and MW513(all NGs);
- Checks into three files (for each MW) if the latest build name is there;
- If not there we are not up-to date. So the script will create the build folder locally;
- For each folder in remote, the script will create the folder locally and download the files inside it. Always respecting the 
structure locally and the list of folders that shouldn't be downloaded (not a copy from remote to local);
- After that, it put the build name on respective MW file from step 2;  
- Script will run between 7pm and 7am inside QA server;
- Its not recursive since we need to maintain the structure of folders locally (to not crash the app that flash set-top boxes)    


### External Libs 
Paramiko and tqdm (not essential)


### Future implementation
- Should have a specific file that handle with logs (today all files import it);
- Should fix and test the Open Stack manager. With this new process, we should handle SFTP and Open Stack.\
To do that it's necessary to check the emails and look for the links with the builds to download from there.\
Another way is look for the JIRA ticket and go through directly. 
