from dashboard_02form import CMSStatus
from flask import Flask, render_template
from flask_wtf import FlaskForm

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

class TableElement(FlaskForm):
    formheader = ['CMS', 'FW','Uptime(hours)','ModuleStatus','WebRTCCalls','LyncCalls','SIPCalls','ActiveMeetings','InboundBW(Mbps)','OutboundBW(Mbps)','Alarms']
    CMSdata = []

# Platform dashboard start ***

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

    return render_template('contact.html', data=data)

if __name__ == '__main__':
    app.run(debug = True)

