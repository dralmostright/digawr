class Config:
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dbdash.db'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'pythonkaka@gmail.com'
    MAIL_PASSWORD = 'python@1234'
    ENCRYPT_KEY = b'5791628bb0b13ce0c676dfde280ba245'
    ABSOLUTE_DATABASE_URI = 'C:/Users/dralm/Workspace/Projects/digawr/dbdash/dbdash.db'
    #MAIL_USERNAME = os.environ.get('EMAIL_USER')