import paramiko
# 'scp' must be installed with pip or in PyCharm interpreter
from scp import SCPClient

#default paramiko config
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#testing linux VM
ssh.connect("192.168.198.142", port=22, username="pfne", password="pfne",
            look_for_keys=False, allow_agent=False)

#create 'scp' variable that calls SCPClient function over paramiko transport established by 'ssh'
scp = SCPClient(ssh.get_transport())


# to UPLOAD FILE from this PC to remote device
# ("from where" "to where"):
# on Windows it is '\\' used when on linux is '/' for paths
scp.put("C:\\Users\\dkorotk\\Desktop\\test.txt", "/home/pfne/scp_test/test.txt")


# to UPLOAD Directory from this PC to remote device
# 'recursive' means copy all the content of this directory
# WARNING! it can overwrite files inside of directory
scp.put("C:\\Users\\dkorotk\\PycharmProjects\\Giraffe\\venv\\den", recursive=True, remote_path="/home/pfne/")


# to DOWNLOAD FILE from remote device to this PC
scp.get("/home/pfne/scp_test/test-from-VM.txt", "C:\\Users\\dkorotk\\Desktop\\")


# always close connection at end
scp.close()
