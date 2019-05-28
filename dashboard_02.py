import psutil
import time
from threading import Lock
from flask import Flask, render_template,request
from flask_socketio import SocketIO
from dashboard_02form import TableElement
from lxml import etree
from dashboard_02form import CMSStatus
from API_SSH import API

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

# Platform dashboard start ***

# 后台线程 产生数据，即刻推送至前端
def background_thread():
    param_status = ["version", "uptime", "mediaStatus", "numClientCalls", "numLyncCalls", "numSipCalls", "numConfs",
                    "mediaBitRateOutgoing", "mediaBitRateIncoming", "alarms"]
    count = 0
    i=0
    CMSName_IPs=['144.131.216.94','144.131.216.96']
    CMSdata = [['CLT01', 1, 2, 3, 4,5,6,7,8,9,10],['CLT02', 0, 1, 2, 3,4,5,6,7,8,9]]
    while True:
        socketio.sleep(5)
        count += 1
        t = time.strftime('%M:%S', time.localtime())
        i+=1
        def CMSplusone(CMSdata):
            for n,oneCMSData in enumerate(CMSdata):
                # for n,element in enumerate(oneCMSData):
                #     if n != 0:
                #         oneCMSData[n] +=1
                CMS = CMSStatus(CMSName_IPs[n], 443, 'admin', 'admin', param_status)
                try:
                    print(CMS.status())
                    print(oneCMSData[1:]+'8888')
                    oneCMSData[1:]=CMS.status()
                    print(oneCMSData[1:])
                except Exception as error:
                    oneCMSData[1:]=['-']*10
                    print(error)
            return (CMSdata)
        result=CMSplusone(CMSdata)

        cpus=result
        # 获取系统cpu使用率 non-blocking
        socketio.emit('server_response',
                      {'data': [t, cpus]},
                      namespace='/platformdashboardconnect')
        # 注意：这里不需要客户端连接的上下文，默认 broadcast = True


@app.route('/platformDashboard',methods=['GET'])
def platformDashboard():
    form=TableElement()
    if request.method == 'GET':
        return render_template('dashboard_02.html', form=form, async_mode=socketio.async_mode)


@socketio.on('connect', namespace='/platformdashboardconnect')
def platform_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)

## Platform dashboard end ***

if __name__ == '__main__':
    socketio.run(app, debug=True)