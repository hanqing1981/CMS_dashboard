from app import app
from flask import render_template

from app.com.telstra.tools.cms.client.CmsClient import CmsClient

clients = [
    # CmsClient('test', '10.79.246.177', 8443, 'admin', 'xxx')
]

@app.route('/dashboard')
def dashboard():
    statusList = []

    for client in clients:
        try:
            status = client.status()
            statusList.append(status)
        except Exception as e:
            print(e.message)

    print(statusList)

    return render_template("dashboard.html",
                           statusList=statusList)
