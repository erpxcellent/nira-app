import os


class Config:
    
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True


    SECRET_KEY = os.environ.get("SECRET_KEY", "oasis-nira-demo")
    
    # DATABASE CONFIGURATION
    DB_URL = "localhost"
    DB_NAME = 'niraDB' # os.environ.get('NIRA_DB_NAME')
    DB_USER = 'root' # os.environ.get('NIRA_DB_USER')
    DB_PW = 'root123' # os.environ.get('NIRA_DB_PW')


    

    SQLITE_DB_URI= 'sqlite:///site.db'
    POSTGRES_DB_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PW}@{DB_URL}/{DB_NAME}'
    MYSQL_DB_URI = f'mysql://{DB_USER}:{DB_PW}@{DB_URL}/{DB_NAME}'


    SQLALCHEMY_DATABASE_URI = MYSQL_DB_URI


    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Allow deployments to increase/decrease the daily capacity without code changes.
    DAILY_APPOINTMENT_LIMIT = int(os.environ.get("DAILY_APPOINTMENT_LIMIT", 20))
    BOOKING_WINDOW_DAYS = int(os.environ.get("BOOKING_WINDOW_DAYS", 30))





    # Mail Configuration 
    # MAIL_SERVER = 'smtp.googlemail.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get('EMAIL_USER')
    # MAIL_PASSWORD = os.environ.get('EMAIL_PASS')



# basedir = os.path.abspath(os.path.dirname(__file__))



class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
