from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from azure.servicebus import ServiceBusClient


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

app.secret_key = app.config.get('SECRET_KEY')

servicebus_client = ServiceBusClient.from_connection_string(conn_str=app.config.get('SERVICE_BUS_CONNECTION_STRING'))


db = SQLAlchemy(app)

from . import routes