Description:
Used to move object config on firewalls between different pools.
Implemented action by action specified in ./task/task.yml
Saves backup of config to ./backups if config push was executed.

Usage: 
run.py [-h] [-D]

optional arguments:
  -h, --help    show this help message and exit
  -D, --deploy  Use to push new config (<Y|n> will be asked)
