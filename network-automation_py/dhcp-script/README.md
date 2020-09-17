### Description
Netmiko-based script to propagate DHCP-helpers config across PDX1 access switches. Made as part of [NETENG-2040](https://jira.dreamhost.com/browse/NETENG-2040).
Config backups will be saved to **backup/**: separate textfile for each device. 

**Requirements**: Python 3.6

### Usage
* Test and print suggested config: ```python run.py -u <username>``` 
* Push config: ```python run.py -u <username> -D```
* Rollback changes: ``` python run.py -u <username> -R -D``` 

### Args
```run.py [-h] -u USERNAME [-D] [-R]``` 

 *required arguments*:
  ``` 
  -u USERNAME, --username   Username for network devices
  ``` 

 *optional arguments*:
  ``` 
  -h, --help                Show this help message and exit
  -D, --deploy              Force pushing new config. Disabled by default
  -R, --rollback            Delete dhcp-helper config
  ``` 