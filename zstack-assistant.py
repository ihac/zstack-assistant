#!/usr/bin/env python
# encoding: utf-8
#
# File name: vm-pa.py
# Author: Mingyu
# Date created: 10/10/2016
# Date last modified: 10/10/2016
# Python Version: 2.7
#
import sys
import json
import getpass
import subprocess

# functions
def hint():
    """hint() will print the usage of this program

    : no input args
    :returns: None

    """
    print '\n\nWhat can I do for you?'
    print '    1. Recover VMs'
    print '    2. Clone VM'
    print '    3. Change IP of VM'
    print '    4. Change description of VM'
    print '    0. Exit'
    print '\n'

def execCmd(cmd):
    """execCmd() will execute the input shell command, load the output into a JSON object and return it

    :cmd: the command to execute
    :returns: JSON object or None
    """
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    out, err = p.communicate()
    try:
        jsonObj = json.loads(out)
        return jsonObj
    except:
        return None

def stopVM(uuid):
    """stopVM() will change VM's state to Stopped

    :uuid: identifier of VM
    :returns: True/False

    """
    uuidArg = "uuid=%s" % uuid
    changeStateToStoppedCmd = ['zstack-cli', 'UpdateVmInstance', uuidArg, 'state=Stopped']
    print '--- change VM {0} state to Stopped ...'.format(uuid),
    sys.stdout.flush()
    res = execCmd(changeStateToStoppedCmd)
    if res is None:
	print 'FAIL'
        return False
    elif res['success'] == True:
	    print 'DONE'
    return True

def startVM(uuid):
    """stopVM() will start a VM

    :uuid: identifier of VM
    :returns: True/False

    """
    uuidArg = "uuid=%s" % uuid
    startVMCmd = ['zstack-cli', 'StartVmInstance', uuidArg]
    print '--- change VM {0} state to Running ...'.format(uuid),
    sys.stdout.flush()
    res = execCmd(startVMCmd)
    if res is None:
	print 'FAIL'
        return False
    elif res['success'] == True:
	    print 'DONE'
    return True

def createImageFromRootVolume(name, volUuid):
    """createImageFromRootVolume() will create a new image from the specified root volume

    :name: name of the new image
    :volUuid: uuid of root volume
    :returns: True/False

    """
    nameArg = "name=%s" % name
    volUuidArg = "rootVolumeUuid=%s" % volUuid
    print '--- create image {0} from root volume ...'.format(name),
    sys.stdout.flush()
    createImageFRVCmd = ['zstack-cli', 'CreateRootVolumeTemplateFromRootVolume', nameArg, volUuidArg]
    res = execCmd(createImageFRVCmd)
    if res is None:
	print 'FAIL'
        return False
    elif res['success'] == True:
	    print 'DONE'
    return True

def setStaticIP(uuid, l3NetworkUuid, ip):
    """setStaticIP() will set the specified VM's ip address

    :uuid: identifier of VM
    :l3NetworkUuid: identifier of l3Network
    :ip: the ip address to set
    :returns: True/False

    """
    ipArg = "ip=%s" % ip
    vmUuidArg = "vmInstanceUuid=%s" % uuid
    l3NetworkUuidArg = "l3NetworkUuid=%s" % l3NetworkUuid
    print '--- set static ip for VM {0} ...'.format(uuid),
    sys.stdout.flush()
    setStaticIPCmd = ['zstack-cli', 'SetVmStaticIp', ipArg, vmUuidArg, l3NetworkUuidArg]
    res = execCmd(setStaticIPCmd)
    if res is None:
	print 'FAIL'
        return False
    elif res['success'] == True:
	    print 'DONE'
    return True

def setDescription(uuid, description):
    """setDescription will set the specified VM's description

    :uuid: identifier of VM
    :description: the description to set
    :returns: True/False

    """
    uuidArg = "uuid=%s" % uuid
    descriptionArg = "description=\"%s\"" % description
    print '--- description for VM {0} ...'.format(uuid),
    sys.stdout.flush()
    setDescriptionCmd = ['zstack-cli', 'UpdateVmInstance', uuidArg, descriptionArg]
    res = execCmd(setDescriptionCmd)
    if res is None:
	print 'FAIL'
        return False
    elif res['success'] == True:
	    print 'DONE'
    return True


def logInByAccount():
    """logInByAccount() will try to login by account. It returns when login successfully or sink into infinite loop when failed

    :returns: None
    """
    while True:
        account = "accountName=%s" % raw_input('Account Name: ')
        password = "password=%s" % getpass.getpass('Password: ')
        loginCmd = ['zstack-cli', 'LogInByAccount', account, password]
        res = execCmd(loginCmd)
        if res is None:
            print 'Login failed: accountName or password is wrong for ZStack'
        elif res['success'] == True:
            print 'Login successfully!'
            break
    return

def queryVmByState(state):
    """queryVmByState() will query vm instances which are in specified state

    :state: Created, Starting, Running, Stopping, Stopped, Unknown, Rebooting, Migrating, Destroyed
    :returns: JSON-formated output of query command if succeed or None if fail

    """
    stateArg = "state=%s" % state
    queryVMCmd = ['zstack-cli', 'QueryVmInstance', stateArg]

    return execCmd(queryVMCmd)

def queryVmByIp(ip):
    """queryVmByIp() will query vm instance with specified ip

    :ip: vm's ip address
    :returns: JSON-formated output of query command if succeed or None if fail

    """
    ipArg = "vmNics.ip=%s" % ip
    queryVMCmd = ['zstack-cli', 'QueryVmInstance', ipArg]

    return execCmd(queryVMCmd)


def recoverVM_OP(uuid):
    """recoverVM_OP() will change VM's state from Unknown to Stopped, and then start VM instance by invoking zstack-cli command.

    :uuid: identifier of VM
    :returns: True/False
    """
    return stopVM(uuid) and startVM(uuid)

def recoverVM():
    """recoverVM() will try to recover VMs from those crashed compute nodes

    : no input args
    :returns: 1

    """
    a, b, c = 0, 0, 0
    queryRes = queryVmByState('Unknown')
    if queryRes is None:
        print 'Query VMs failed. Please check your source code.'
    elif queryRes['success'] == True:
        if len(queryRes['inventories']) == 0:
            print 'No VM is in Unknown state'
        else:
            for vmDat in queryRes['inventories']:
                a = a + 1
                uuid = vmDat['uuid']
                name = vmDat['name']
                print '\nVM {0} with uuid {1} is in Unknown state. Are you sure to recover it?'.format(name, uuid)
                if raw_input('y/n: ') == 'y':
                    print 'Recover VM {0} now...'.format(name)
                    if recoverVM_OP(uuid) == True:
                        print 'Recover VM with uuid {0} successfully.'.format(uuid)
                        b = b + 1
                    else:
                        print 'Recover VM with uuid {0} failed.'.format(uuid)
                        c = c + 1
                else:
                    print 'Skip VM {0}.'.format(name)
    print '>>> Alltogether {0} VMs are in Unknown state'.format(a)
    print '>>> Alltogether {0} VMs have been recoverd'.format(b)
    print '>>> Alltogether {0} VMs fail to be recovered'.format(c)
    return 1

def cloneVM_OP(name, uuid, volUuid):
    """cloneVM_OP() will stop the specified VM, make a copy from its root volume, and finally create a new VM from the copy

    :name: name of VM
    :uuid: identifier of VM
    :volUuid: identifier of root volume
    :returns: True/False

    """
    volName = "image-%s" % name
    return stopVM(uuid) and createImageFromRootVolume(volName, volUuid)


def cloneVM():
    """cloneVM() will try to create an image from a living VM and then start a new VM from the image

    : no input args
    :returns: 2

    """
    ip = raw_input('Which vm do you want to clone? Please input its ip: ')
    queryRes = queryVmByIp(ip)
    if queryRes is None:
        print 'Query VMs failed. Please check your source code.'
    elif queryRes['success'] == True:
        if len(queryRes['inventories']) == 0:
            print 'No VM has ip {0}'.format(ip)
        else:
            for vmDat in queryRes['inventories']:
                uuid = vmDat['uuid']
                name = vmDat['name']
                volUuid = vmDat['rootVolumeUuid']
                print '\nVM {0} with uuid {1} has ip {2}. Are you sure to stop and clone it?'.format(name, uuid, ip)
                if raw_input('y/n: ') == 'y':
                    print 'Clone VM {0} now...'.format(name)
                    if cloneVM_OP(name, uuid, volUuid):
                        print 'Clone VM with uuid {0} successfully.'.format(uuid)
                        print '>>> Now you can create new VM instances from image-{0} on Web UI.'.format(name)
                    else:
                        print 'Clone VM with uuid {0} failed.'.format(uuid)
                else:
                    print 'Cancel to clone VM {0}'.format(name)
    return 2

def changeIP_OP(uuid, l3NetworkUuid, newIP):
    """changeIP_OP() will invoke setStaticIP function to change the spcified VM's ip address

    :uuid: identifier of VM
    :l3NetworkUuid: identifier of l3Network
    :newIP: new ip address of VM
    :returns: True/False

    """
    return stopVM(uuid) and setStaticIP(uuid, l3NetworkUuid, newIP)

def changeIP():
    """changeIP() will modify the specified VM's ip address

    :returns: 3

    """
    ip = raw_input('Which vm do you want to modify? Please input its ip: ')
    queryRes = queryVmByIp(ip)
    if queryRes is None:
        print 'Query VMs failed. Please check your source code.'
    elif queryRes['success'] == True:
        if len(queryRes['inventories']) == 0:
            print 'No VM has ip {0}'.format(ip)
        else:
            for vmDat in queryRes['inventories']:
                uuid = vmDat['uuid']
                name = vmDat['name']
                l3NetworkUuid = vmDat['defaultL3NetworkUuid']
                print '\nVM {0} with uuid {1} has ip {2}. Are you sure to change its ip?'.format(name, uuid, ip)
                if raw_input('y/n: ') == 'y':
                    newIP = raw_input('Please input the new ip for this VM: ')
                    print 'Change VM {0}\'s IP now...'.format(name)
                    if changeIP_OP(uuid, l3NetworkUuid, newIP):
                        print 'Change IP to {0} successfully.'.format(newIP)
                        print '>>> Now VM {0} has a new ip address: {1}.'.format(name, newIP)
                    else:
                        print 'Change IP to {0} failed.'.format(newIP)
                else:
                    print 'Cancel to change VM {0}\'s IP'.format(name)
    return 3


def changeDescription_OP(uuid, newDescription):
    """changeDescription_OP() will invoke setDescription function to change the spcified VM's description

    :uuid: identifier of VM
    :newDescription: new description of VM
    :returns: True/False

    """
    return setDescription(uuid, newDescription)

def changeDescription():
    """changeIP() will modify the specified VM's ip address

    :returns: 3

    """
    ip = raw_input('Which vm do you want to modify? Please input its ip: ')
    queryRes = queryVmByIp(ip)
    if queryRes is None:
        print 'Query VMs failed. Please check your source code.'
    elif queryRes['success'] == True:
        if len(queryRes['inventories']) == 0:
            print 'No VM has ip {0}'.format(ip)
        else:
            for vmDat in queryRes['inventories']:
                uuid = vmDat['uuid']
                name = vmDat['name']
                print '\nVM {0} with uuid {1} has ip {2}. Are you sure to change its description?'.format(name, uuid, ip)
                if raw_input('y/n: ') == 'y':
                    newDescription = raw_input('Please input the new description for this VM: ')
                    print 'Change VM {0}\'s description now...'.format(name)
                    if changeDescription_OP(uuid, newDescription):
                        print 'Change description successfully.'
                        print '>>> Now VM {0} has a new description: {1}.'.format(name, newDescription)
                    else:
                        print 'Change description failed.'
                else:
                    print 'Cancel to change description'
    return 4
#
# main
#
if __name__ == '__main__':
    print '\n>>> Welcome to use ZStack-Assistant <<<'
    logInByAccount()
    while True:
        hint()
        choise = raw_input('Please select one function: ')
        func = {
            '1': recoverVM,
            '2': cloneVM,
            '3': changeIP,
            '4': changeDescription,
            '0': exit,
        }.get(choise, None)
        if func is None:
            continue
        else:
	        func()



