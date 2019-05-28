from threading import Lock

import urllib3
from dashboard_02form import CMSStatus
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask_wtf import FlaskForm
from wtforms import StringField

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TableElement(FlaskForm):
    formheader = ['CMS', 'FW','Uptime(hours)','ModuleStatus','WebRTCCalls','LyncCalls','SIPCalls','ActiveMeetings','InboundBW(Mbps)','OutboundBW(Mbps)','Alarms']
    CMSdata = []

# Platform dashboard start ***

# 后台线程 产生数据，即刻推送至前端
def background_thread():
    param_status = ["version", "uptime", "mediaStatus", "numClientCalls", "numLyncCalls", "numSipCalls", "numConfs",
                    "mediaBitRateOutgoing", "mediaBitRateIncoming", "alarms"]
    count = 0
    i=0
    # CMSdata = [['CLT01', 1, 2, 3, 4,5,6,7,8,9,10],['CLT02', 0, 1, 2, 3,4,5,6,7,8,9]]

    clients = [
        CMSStatus('CTL01', '144.131.216.94', 443, 'admin', 'admin', param_status),
        CMSStatus('CTL02', '144.131.216.96', 443, 'admin', 'admin', param_status)
    ]

    form = TableElement()
    while True:
        socketio.sleep(5)

        for i, client in enumerate(clients):
            try:
                client.login()
                form.cmsData.append(client.status())
            except Exception as e:
                print(e)
        print(form)
        socketio.emit('server_response',
                      {'data': form},
                      namespace='/platformdashboardconnect')
    # CLT01.login()
    # CLT02.login()
    # while True:
    #     socketio.sleep(5)
    #     count += 1
    #     t = time.strftime('%M:%S', time.localtime())
    #     # print(CLT01.status())
    #     # print(CLT02.status())
    #     CMSdata[0][1:] = CLT01.status()
    #     CMSdata[1][1:] = CLT02.status()
    #
    #
    #     # def CMSplusone(CMSdata):
    #     #     for n,oneCMSData in enumerate(CMSdata):
    #     #         # for n,element in enumerate(oneCMSData):
    #     #         #     if n != 0:
    #     #         #         oneCMSData[n] +=1
    #     #         CMS = CMSStatus(CMSName_IPs[n], 443, 'admin', 'admin', param_status)
    #     #         try:
    #     #             print(CMS.status())
    #     #             print(oneCMSData[1:]+'8888')
    #     #             oneCMSData[1:]=CMS.status()
    #     #             print(oneCMSData[1:])
    #     #         except Exception as error:
    #     #             oneCMSData[1:]=['-']*10
    #     #             print(error)
    #     #     return (CMSdata)
    #     print(CMSdata)
    #     result=CMSdata
    #
    #     cpus=result
    #     # 获取系统cpu使用率 non-blocking
    #     socketio.emit('server_response',
    #                   {'data': [t, cpus]},
    #                   namespace='/platformdashboardconnect')
    #     # 注意：这里不需要客户端连接的上下文，默认 broadcast = True


@app.route('/platformDashboard',methods=['GET'])
def platformDashboard():
    form=TableElement()
    if request.method == 'GET':
        return render_template('dashboard_02.html', form=form, async_mode=socketio.async_mode)

@app.route('/platformDashboard/status',methods=['GET'])
def platformDashboard():
    clients = [
        CMSStatus('CTL01', '144.131.216.94', 443, 'admin', 'admin'),
        CMSStatus('CTL02', '144.131.216.96', 443, 'admin', 'admin')
    ]

    data = []
    for i, client in enumerate(clients):
        try:
            client.login()
            data.append(client.status())
        except Exception as e:
            print(e)
    return data

# @socketio.on('connect', namespace='/platformdashboardconnect')
# def platform_connect():
#     global thread
#     with thread_lock:
#         if thread is None:
#             thread = socketio.start_background_task(target=background_thread)

## Platform dashboard end ***

if __name__ == '__main__':
    socketio.run(app, debug=True)