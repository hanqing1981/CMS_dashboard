import re
import time
from lxml import etree

import requests


class CmsStatus:
    version = None
    uptime = None
    mediaStatus = None
    numClientCalls = None
    numLyncCalls = None
    numSipCalls = None
    numConfs = None
    mediaBitRateOutgoing = None
    mediaBitRateIncoming = None

class CmsAlarm:
    alarm = None

class CmsClient():
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
        statusHeader = {
            "Cookie": self.authenticateResponse.headers['Set-Cookie']
        }
        url = 'https://{}:{}/index.xml?_={}'.format(self.hostname, self.port, int(time.time() * 1000))
        self.statusResponse=requests.request('GET', url, verify=False, headers=statusHeader)

        status = CmsStatus

        data = etree.XML(self.statusResponse.content)

        status.uptime = data.xpath('/data/statusTable[@id="status"]/entries/entry[@id="uptime"]/value')[0].text
        status.version = data.xpath('/data/statusTable[@id="status"]/entries/entry[@id="version"]/value')[0].text
        status.mediaStatus = data.xpath('/data/statusTable[@id="status"]/entries/entry[@id="mediaStatus"]/value')[0].text
        status.numClientCalls = data.xpath('/data/statusTable[@id="status"]/entries/entry[@id="numClientCalls"]/value')[0].text
        status.numLyncCalls = data.xpath('/data/statusTable[@id="status"]/entries/entry[@id="numLyncCalls"]/value')[0].text
        status.numSipCalls = data.xpath('/data/statusTable[@id="status"]/entries/entry[@id="numSipCalls"]/value')[0].text
        status.numConfs = data.xpath('/data/statusTable[@id="status"]/entries/entry[@id="numConfs"]/value')[0].text
        status.mediaBitRateOutgoing = data.xpath('/data/statusTable[@id="status"]/entries/entry[@id="mediaBitRateOutgoing"]/value')[0].text
        status.mediaBitRateIncoming = data.xpath('/data/statusTable[@id="status"]/entries/entry[@id="mediaBitRateIncoming"]/value')[0].text

        return status

    def alarms(self):  # request status page with real cookie
        statusHeader = {
            "Cookie": self.authenticateResponse.headers['Set-Cookie']
        }
        url = 'https://{}:{}/alarms.xml'.format(self.hostname, self.port, int(time.time() * 1000))
        self.alarmsResponse=requests.request('POST', url, verify=False, headers=statusHeader)

        print(self.alarmsResponse.content)


if __name__=='__main__':
    client = CmsClient('144.131.216.96', '144.131.216.96', 443, 'admin', 'admin')
    client.login()
    client.alarms()