from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField


class TableElement(FlaskForm):
    formheader = ['CMS', 'FW', 'Uptime(days)', 'Calls', 'InboundBW(Mbps)', 'OutboundBW(Mbps)', 'Alarms', 'Utilization(%)']
    CLT01data=[StringField('CLT01') for i in range(len(formheader))]
    CLT02data = [StringField('CLT02') for i in range(len(formheader))]
    CMSdata = [CLT01data,CLT02data]
    CMSnames=['CLT01','CLT02']
    for n,CMS in enumerate(CMSdata):
        for element in CMS:
            element.data=CMSnames[n]




def getPlatformData(CMSLogin,CMSInfor):
    returndata=[]
    def oneCMSData():
        for CMSLoginInfo in CMSLogin['CMSlogin']:
            ip=CMSLoginInfo[1]
            username=CMSLoginInfo[2]
            password=CMSLoginInfo[3]
        return (ip,username,password)
    ip,username,password=oneCMSData()
    try:
        api = API.Get_put_post(ip, username, password)
    except Exception as error:
        print(error)
        return ([CMSLogin['CMSlogin'][0],'-','-','-','-','-','-','-'])
    AllStatusData=api.get(subject=CMSInfor['system'][0])
    AllAlarms=api.get(subject=CMSInfor['alarms'][0])
    AllLoad=api.get(subject=CMSInfor['load'][0])
    AllLoadLimit=api.get(subject=CMSInfor['loadlimit'][0])
    for k,v in CMSInfor:
        for para in v:
            returndata.append(AllStatusData.xpath('//softwareversion'))

    return (returndata)




if __name__=='__main__':
    from API_SSH import API

    CMSInfor={}
    CMSInfor={}
    CMSLogin={'CMSlogin':['CLT01','144.131.216.96','admin','admin'],}
    CMSInfor={
              'system':['system/status',['softwareversion','uptimeseconds','calllegsactive','audiobitrateoutgoing'
                                           ,'videobitrateoutgoing','audiobitrateincoming','videobitrateincoming']],
              'alarms':['system/alarms',['total']],
              'load':['system/load',['load']],
              'loadlimit':['system/configuration/cluster',['loadlimit']]
              }
    CMSdata=getPlatformData(CMSLogin,CMSInfor)
    print(CMSdata)

