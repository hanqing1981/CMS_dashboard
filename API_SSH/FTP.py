import paramiko
import os
import configparser
import logging


logging.basicConfig(filename="C:/Users/d322501/Downloads/logging/systemlogs.txt",
                    format='levelname:%(levelname)s filename: %(filename)s '
                           'outputNumber: [%(lineno)d]  func: %(funcName)s output msg:  %(message)s'
                           ' - %(asctime)s', datefmt='[%d/%b/%Y %H:%M:%S]', level=logging.INFO)

def sftp_download(cmsip=None,login=None,syspath=None,filenames=None,filetypes=None,newfilename=None):
    t = paramiko.Transport((cmsip, 22))
    try:
        t.connect(username=login['username'], password=login['password'])
        sftp = paramiko.SFTPClient.from_transport(t)
    except Exception as error:
        raise error
    if filenames:
        for filename in filenames:
            sftp.get(r'/%s' %filename, r'%s' %(syspath+'/'+newfilename))
    elif filetypes:
        pass
    t.close()

def sftp_download_check(cmsip=None,login=None,syspath=None,filenames=None,newfilename=None):
    t = paramiko.Transport((cmsip, 22))
    try:
        t.connect(username=login['username'], password=login['password'])
        sftp = paramiko.SFTPClient.from_transport(t)
    except Exception as error:
        raise error
    if filenames:
        for filename in filenames:
            ofilezie=sftp.stat(r'/%s' %filename).st_size
            nfilesize = os.stat(r'%s' % (syspath + '/' + newfilename)).st_size

        if int(nfilesize)<((int(ofilezie))/2):
            return ('file size is too small')
        else:
            return (200)
    t.close


def sftp_upload(login,server,uploadlocalfilepath,filename):
    serverlogin = {}
    serverlogin['username'] = login['username']
    serverlogin['password'] = login['password']

    try:
        s=paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(server,22,username=serverlogin['username'],password=serverlogin['password'])
        sftp = s.open_sftp()
        logging.info('ftp starts for:' + server)

    # try:
    #     t = paramiko.Transport((server, 22))
    #     print(t.open_sftp_client())
    #     t.connect(**serverlogin)
    #     sftp = paramiko.SFTPClient.from_transport(t)
    #     logging.info('sftpalex', sftp)
    except Exception as error:
        logging.error(server, error)
    else:
        try:
            sftp.put(uploadlocalfilepath, r'/%s' % filename)
        except Exception as e:
            logging.error(server, e)
            logging.info('ftp ends for:' + server)
        sftp.close()


if __name__=='__main__':
    login = {}
    login['username'] = 'admin'
    login['password'] = 'admin'
    server = '144.131.216.96'
    uploadlocalfilepath = 'C:/Users/d322501/Downloads/images/upgrade.img'
    filename = 'upgrade.img'
    sftp_upload(login, server, uploadlocalfilepath, filename)




