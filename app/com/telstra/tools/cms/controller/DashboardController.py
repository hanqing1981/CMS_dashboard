from app import app
from flask import render_template

from app.com.telstra.tools.cms.client.CmsClient import CmsClient


clients = [
    CmsClient('CLT02', '144.131.216.96', 443, 'admin', 'admin'),
    CmsClient('CLT01', '144.131.216.94', 443, 'admin', 'admin')
]

@app.route('/dashboard')
def dashboard():
    statusList = []

    for client in clients:
        try:
            status = client.status()
            status.alarms=client.alarms()
            statusList.append(status)
        except Exception as e:
            print(e.message)
            status = client.status()
            statusList.append(status)

    # print(statusList)

    return render_template("dashboard.html",
                           statusList=statusList)
