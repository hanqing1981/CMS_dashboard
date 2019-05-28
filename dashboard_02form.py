import time
import requests
import re
from lxml import etree

class CMSStatus():
    param_status = ["version", "uptime", "mediaStatus", "numClientCalls", "numLyncCalls", "numSipCalls", "numConfs",
                    "mediaBitRateOutgoing", "mediaBitRateIncoming", "alarms"]

    def __init__(self, name, hostname, port, username, password):
        self.name = name
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

    def __obtainSession(self):  # request login page to get first Cookie and session key
        try:
            url = 'https://{}:{}/authenticate.html'.format(self.hostname, self.port)
            self.initResponse = requests.request('GET', url, verify=False)
            self.acanoSessionKey = re.findall('<input type="hidden" name ="Acano-Session-Key" value ="(.*?)"/>', str(self.initResponse.content))[0]
        except:
            raise Exception('authenticate.html is blocked')
    def login(self):  # request /authenticate.html page to get real cookie,
        self.__obtainSession()

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

    def status(self):  # request status page with real cookie
        self.all_status=[self.name]

        statusHeader = {
            "Cookie": self.authenticateResponse.headers['Set-Cookie']
        }
        url = 'https://{}:{}/index.xml?_={}'.format(self.hostname, self.port, int(time.time() * 1000))
        self.statusResponse=requests.get(url, verify=False, headers=statusHeader)

        htmlcontent=etree.HTML(self.statusResponse.content)
        print('*****************')
        for e in self.param_status:
            if e =='uptime':
                self.all_status.append('-')
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
        return (self.all_status)

if __name__=='__main__':
    # from API_SSH import API
    #
    # CMSInfor={}
    # CMSInfor={}
    # CMSLogin={'CMSlogin':['CLT01','144.131.216.96','admin','admin'],}
    # CMSInfor={
    #           'system':['system/status',['softwareversion','uptimeseconds','','calllegsactive','audiobitrateoutgoing'
    #                                        ,'videobitrateoutgoing','audiobitrateincoming','videobitrateincoming']],
    #           'alarms':['system/alarms',['total']],
    #           'load':['system/load',['load']],
    #           'loadlimit':['system/configuration/cluster',['loadlimit']]
    #           }
    # CMSdata=getPlatformData(CMSLogin,CMSInfor)
    # print(CMSdata)


    param_status = []
    param_status = ["version", "uptime", "mediaStatus", "numClientCalls", "numLyncCalls", "numSipCalls", "numConfs",
                    "mediaBitRateOutgoing", "mediaBitRateIncoming", "alarms"]
    CMS = CMSStatus('144.131.216.96', 443, 'admin', 'admin', param_status)
    CMS.status()