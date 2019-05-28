from flask import Flask

app = Flask(__name__)

from app.com.telstra.tools.cms.controller import DashboardController
