import re
import time
import requests
import xmltodict
from app.com.telstra.tools.cms.model.CmsStatus import CmsStatus,CmsStatusDefault
from app.com.telstra.tools.cms.model.API import Get_put_post

# obtain cms/index.html page information

# CMS needs two cookies to get index page


class CmsClient():
    __session = None

    def __init__(self, name, hostname, port, username, password):
        self.name = name
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

    def __obtainSession(self):  # GET login page to get first Cookie (in header) and acanoSessionKey - do it via browswer not postman
        try:
            url = 'https://{}:{}/authenticate.html'.format(self.hostname, self.port)
            initResponse = requests.request('GET', url, verify=False)
            acanoSessionKey = re.findall('<input type="hidden" name ="Acano-Session-Key" value ="(.*?)"/>', str(initResponse.content))[0]
            return {
                'unrealSession': initResponse.headers['Set-Cookie'],
                'acanoSessionKey': acanoSessionKey
            }
        except Exception as e:
            raise Exception('authenticate.html is blocked')
    def __checkSession(self):
        if self.__session == None:
            print('session is null, to obtain a new session')
            return False

        try:
            url = 'https://{}:{}/chauthtok.xml?_={}'.format(self.hostname, self.port, int(time.time() * 1000)) # login page after authetication
            header = {
                "Cookie": self.__session
            }
            chauthtokResponse=requests.request('GET', url, verify=False, headers=header)
            data = xmltodict.parse(chauthtokResponse.content)
            data['data']['menu']   # check if the item is available or not, if yes, then session is still valid
        except:
            print('the old session is not available')
            return False

        print('the old session is available')
        return True

    def __login(self):  # request /authenticate.html page to get real cookie (second cookie)
        if not self.__checkSession():
            validateData = self.__obtainSession()

            url = 'https://{}:{}/authenticate.html'.format(self.hostname, self.port)
            header = {
                "Content-Type": "application/x-www-form-urlencoded",    # tell remote server on what type of content in the request body
                "Cookie": validateData['unrealSession']
            }
            data = {
                '0': self.username,
                '1': self.password,
                'Acano-Session-Key': validateData['acanoSessionKey']
            }

            authenticateResponse = requests.request('POST', url, headers=header, data=data, verify=False) # to get real cookie  in header - do it via browser
            # cookie record all connection and authenticaion information. with the cookie, no need authenticate anymore
            self.__session = authenticateResponse.headers['Set-Cookie']

    def status(self):  # request status page with real cookie
        cmsapi=Get_put_post(self.hostname, self.username, self.password)
        self.systemalarms=cmsapi.apiConnTest()
        if self.systemalarms:
            self.connResult=1
        else:
            self.connResult = 0
            return (CmsStatusDefault(self.name))
        try:
            self.__login()
            url = 'https://{}:{}/index.xml?_={}'.format(self.hostname, self.port, int(time.time() * 1000))
            header = {
                "Cookie": self.__session
            }
            statusResponse=requests.request('GET', url, verify=False, headers=header)

            return CmsStatus(self.name, statusResponse.content)
        except Exception as error:
            print (error)
            self.connResult=0
            return (CmsStatusDefault(self.name))



    def alarms(self):
        if self.connResult:
            totalalarms=self.systemalarms.xpath('//alarms/@total')
            return(totalalarms[0])
        else:
            return('-')


if __name__=='__main__':
    client = CmsClient('test', '10.79.246.177', 8443, 'admin', 'C!sc0123')
    status = client.status()

