import urllib3
import time
import requests
import re
from lxml import etree
import logging
from API_SSH import API

# logging.basicConfig(level=logging.NOTSET)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CMSStatus():

    def __init__(self, hostname, port, username, password,param_status):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.param_status=param_status

    def obtainSession(self):  # request login page to get first Cookie and session key
        url = 'https://{}:{}/authenticate.html'.format(self.hostname, self.port)
        self.initResponse = requests.request('GET', url, verify=False)
        self.acanoSessionKey = re.findall('<input type="hidden" name ="Acano-Session-Key" value ="(.*?)"/>', str(self.initResponse.content))[0]
        print(self.initResponse.headers['Set-Cookie'])
        print(self.acanoSessionKey)

    def login(self):  # request /authenticate.html page to get real cookie,
        self.obtainSession()

        url = 'https://{}:{}/authenticate.html'.format(self.hostname, self.port)
        header = {
            "Content-Type": "application/x-www-form-urlencoded",    # tell remote server on what type of content in the request body
            "Cookie": self.initResponse.headers['Set-Cookie']
        }
        data = {
            '0': self.username,
            '1': self.password,
            'Acano-Session-Key': self.acanoSessionKey
        }
        self.authenticateResponse = requests.request('POST', url, headers=header, data=data, verify=False)
        print(self.authenticateResponse.headers['Set-Cookie'])

    def status(self):  # request status page with real cookie
        self.all_status=[]
        self.login()
        statusHeader = {
            "Cookie": self.authenticateResponse.headers['Set-Cookie']
        }
        url = 'https://{}:{}/index.xml?_={}'.format(self.hostname, self.port, int(time.time() * 1000))
        # self.statusResponse = requests.request('GET', url, headers=statusHeader, verify=False)
        self.statusResponse=requests.get(url, verify=False, headers=statusHeader)
        # print(self.statusResponse.text)
        htmlcontent=etree.HTML(self.statusResponse.content)
        print('*****************')
        # print(htmlcontent.xpath(('//entries/entry[@id="mediaStatus"]/value'))[0].text)
        for e in self.param_status:
            if e =='uptime':
                uptime=(htmlcontent.xpath(('//entries/entry[@id="%s"]/value' %e))[0].text)
                uptime=uptime.split(',')
                uptimeHours=0
                realhours=0
                for n,t in enumerate(uptime):
                    t=t.split(' ')
                    if t[1]=='days':
                        t=int(t[-2])
                        t=t*24
                    elif t[1]=='minutes':
                        t=int(t[-2])
                        t=t//60
                    elif t[1]=='seconds':
                        t=int(t[0])
                        t=t//3600
                    else:
                        print(t)
                        t=int(t[-2])
                    uptimeHours +=int(t)
                self.all_status.append(uptimeHours)
            elif e=="alarms":
                api = API.Get_put_post(self.hostname,self.username,self.password)
                htmlalarms=api.get('system/alarms')
                numAlarms=htmlalarms.xpath('//alarms/@total')[0]
                self.all_status.append(numAlarms)
            elif e=="mediaStatus":
                moduleStatus=(htmlcontent.xpath(('//entries/entry[@id="%s"]/value' %e))[0].text)
                moduleStatus=moduleStatus.split(' ')
                self.all_status.append(moduleStatus[0])
            else:
                self.all_status.append(htmlcontent.xpath(('//entries/entry[@id="%s"]/value' %e))[0].text)
        print(self.all_status)


if __name__ == '__main__':
    param_status=[]
    param_status=["version","uptime","mediaStatus","numClientCalls","numLyncCalls","numSipCalls","numConfs",
                  "mediaBitRateOutgoing","mediaBitRateIncoming","alarms"]
    CMS = CMSStatus('144.131.216.94', 443, 'admin', 'admin',param_status)
    CMS.status()
