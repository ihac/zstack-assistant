#!/usr/bin/env python
# encoding: utf-8
#
# File name: vm-pa.py
# Author: Mingyu
# Date created: 10/10/2016
# Date last modified: 10/10/2016
# Python Version: 2.7
#
import json
import getpass
import subprocess

# functions
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

def restartVM(uuid):
    """restartVM() will change VM's state from Unknown to Stopped, and then start VM instance by invoking zstack-cli command.
    :uuid: identifier of VM
    :returns: True/False
    """
    uuidArg = "uuid=%s" % uuid
    changeStateToStoppedCmd = ['zstack-cli', 'UpdateVmInstance', uuidArg, 'state=Stopped']
    startVMCmd = ['zstack-cli', 'StartVmInstance', uuidArg]
    res = execCmd(changeStateToStoppedCmd)
    if res is None:
        print '--- change VM {0} state to Stopped...FAIL'.format(uuid)
        return False
    elif res['success'] == True:
        print '--- change VM {0} state to Stopped...DONE'.format(uuid)
    res = execCmd(startVMCmd)
    if res is None:
        print '--- change VM {0} state to Running...FAIL'.format(uuid)
        return False
    elif res['success'] == True:
        print '--- change VM {0} state to Running...DONE'.format(uuid)
    return True

# LogIn
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

# Query VMs which are in Unknown state
queryVMCmd = ['zstack-cli', 'QueryVmInstance', 'state=Unknown']
jsonDat = execCmd(queryVMCmd)
if jsonDat is None:
    print 'Query VMs failed. Please check your code.'
elif jsonDat['success'] == True:
    if len(jsonDat['inventories']) == 0:
        print 'No VM is in Unknown state'
    else:
        for vmDat in jsonDat['inventories']:
            uuid = vmDat['uuid']
            name = vmDat['name']
            print '\nVM {0} with uuid {1} is in Unknown state. Are you sure to restart it?'.format(name, uuid)
            if raw_input('y/n: ') == 'y':
                print 'Restart VM {0} now...'.format(name)
                if restartVM(uuid) == True:
                    print 'Restart VM with uuid {0} successfully.'.format(uuid)
                else:
                    print 'Restart VM with uuid {0} failed.'.format(uuid)
            else:
                print 'Skip VM {0}.'.format(name)
