import os

app_dir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    DEBUG = True
    POSTGRES_URL="postgres-migration-server.postgres.database.azure.com"
    POSTGRES_USER="azureuser@postgres-migration-server"
    POSTGRES_PW="Samour1995"
    POSTGRES_DB="techconfdb"
    DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or DB_URL
    CONFERENCE_ID = 1
    SECRET_KEY = 'LWd2tzlprdGHCIPHTd4tp5SBFgDszm'
    SERVICE_BUS_CONNECTION_STRING ='Endpoint=sb://sb-migration-namespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=4RhpfZhBZSRaTH4XTjkL7LxKNHIjOfeEPYpd1miPIE0='
    SERVICE_BUS_QUEUE_NAME ='notificationqueue'
    ADMIN_EMAIL_ADDRESS = "samer9abaza5@gmail.com"
    SENDGRID_API_KEY = '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' #Configuration not required, required SendGrid Account

class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False