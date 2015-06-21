#!/usr/bin/env python

import paramiko
import re
import time
import sys
import traceback
from conf.configurations import cisco_username, cisco_password, ip_list

#paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)


def vpn_user_creation(username, ip, vpn_pass):
    #connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=cisco_username, password=cisco_password, allow_agent=False, look_for_keys=False)

    #Interactive shell
    print "In user EXEC mode - " + ip
    remote_conn = ssh.invoke_shell()
    remote_conn.send("enable\n")
    time.sleep(1)
    remote_conn.send(cisco_password + "\n")
    time.sleep(1)
    output = remote_conn.recv(5000)
    if "#"in output:
        print "In privileged EXEC mode"
    else:
        remote_conn.close()
        raise Exception("Error - Could not login to Privileged Exec mode\n" + output)

    #Check if User already exists
    remote_conn.send("show run | inc " + username + "\n")
    time.sleep(1)
    output = remote_conn.recv(5000)
    if ("username " + username + " privilege") in output:
        remote_conn.close()
        raise Exception('Error - the user %s is already exists' % username)
    remote_conn.send(" conf t \n")
    remote_conn.send('username %s privilege 0 secret %s\n' % (username, vpn_pass))
    time.sleep(1)
    remote_conn.send('exit\n')
    remote_conn.send('wr\n')
    print "closing connection"
    remote_conn.close()
    return ('VPN USER - %s \nVPN PASSWORD - %s ' % (username, vpn_pass))


def pass_gen():
    import string
    from random import choice

    characters = string.ascii_letters + string.digits
    password = "".join(choice(characters) for x in xrange(10))
    return password


def main():
    usage = "usage: [--vpn_user First-name_Last-name]"
    args = sys.argv[1:]
    if not args:
        print usage
        sys.exit(1)
    vpn_pass = pass_gen()
    for ip in ip_list:
        if args[0] == '--vpn_user' and re.search(r'\w+\_\w+', args[1]):
            username = (args[1]).lower()
            try:
                print vpn_user_creation(username, ip, vpn_pass)
            except:
                print traceback.print_exc()
            else:
                print usage

if __name__ == "__main__":
    main()
