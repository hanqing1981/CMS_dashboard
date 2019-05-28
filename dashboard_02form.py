from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
import urllib3
import time
import requests
import re
from lxml import etree
from API_SSH import API
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TableElement(FlaskForm):
    formheader = ['CMS', 'FW','Uptime(hours)','ModuleStatus','WebRTCCalls','LyncCalls','SIPCalls','ActiveMeetings','InboundBW(Mbps)','OutboundBW(Mbps)','Alarms']
    CLT01data=[StringField('CLT01') for i in range(len(formheader))]
    CLT02data = [StringField('CLT02') for i in range(len(formheader))]
    CMSdata = [CLT01data,CLT02data]
    CMSnames=['CLT01','CLT02']
    for n,CMS in enumerate(CMSdata):
        for element in CMS:
            element.data=CMSnames[n]


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
        # print(self.initResponse.headers['Set-Cookie'])
        # print(self.acanoSessionKey)

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
                api = API.Get_put_post(self.hostname, self.username, self.password)
                htmluptime = api.get('system/status')
                seconduptime = htmluptime.xpath('//status/uptimeSecond')[0]
                hoursuptime=seconduptime//3600
                self.all_status.append(hoursuptime)
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
    from API_SSH import API

    CMSInfor={}
    CMSInfor={}
    CMSLogin={'CMSlogin':['CLT01','144.131.216.96','admin','admin'],}
    CMSInfor={
              'system':['system/status',['softwareversion','uptimeseconds','','calllegsactive','audiobitrateoutgoing'
                                           ,'videobitrateoutgoing','audiobitrateincoming','videobitrateincoming']],
              'alarms':['system/alarms',['total']],
              'load':['system/load',['load']],
              'loadlimit':['system/configuration/cluster',['loadlimit']]
              }
    CMSdata=getPlatformData(CMSLogin,CMSInfor)
    print(CMSdata)

