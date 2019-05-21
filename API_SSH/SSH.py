import paramiko
import time
import logging


def wait_typein_cli(chan):
    chan.recv_ready()
    time.sleep(3)
    return(chan.recv(1024).decode('utf-8'))



def SshTransport_Command(cmsip=None,login=None,CliComm=None,result=None):

    try:
        client = paramiko.Transport((cmsip, 22))
        client.connect(username=login['username'], password=login['password'])
        chan = client.open_session()
        chan.settimeout(20)
        chan.get_pty()
        chan.invoke_shell()   # need this to make 'chan.send' work
    except Exception as error:
        raise (error)

    try:
        wait_typein_cli(chan)
        for cli in CliComm:
            try:
                chan.send(cli)
                time.sleep(1)
                chan.send('\r\n')
                chan.recv(1024).decode('utf-8')
            except Exception as e:
                print(e)
            output=wait_typein_cli(chan)
            # print(output)
            if result in output[(-100):]:
                return (200)
            else:
                return(output)

    except Exception as error:
        return(error)

    client.close()


def ssh_exec_command(envinfo,server,command):
    serverlogin = {}
    serverlogin['username'] = envinfo['username']
    serverlogin['password'] = envinfo['password']
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=server, **serverlogin)
    except Exception as error:
        logging.error(error)
    else:
        stdin, stdout, stderr = client.exec_command(command)
        outputout=stdout.read()
        outputerror=stderr.read()
        client.close()
        return (outputout, outputerror)



if __name__=='__main__':
    login={}
    login['username']='admin'
    login['password']='admin'
    CliComm=[('backup snapshot 1010')]
    result=SshTransport_Command(cmsip='144.131.216.96',login=login,CliComm=CliComm,result='ready for download')
    print(result)










