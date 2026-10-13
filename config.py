import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Production deployments must provide a private, stable signing key.
    APP_ENV = os.environ.get('APP_ENV', 'development').lower()
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if APP_ENV == 'production' and not SECRET_KEY:
        raise RuntimeError('SECRET_KEY must be set when APP_ENV=production.')
    SECRET_KEY = SECRET_KEY or 'local-development-only-change-before-deploy'

    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', '').strip().lower()
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')
    if APP_ENV == 'production' and not (ADMIN_USERNAME and ADMIN_PASSWORD):
        raise RuntimeError('ADMIN_USERNAME and ADMIN_PASSWORD must be set in production.')
    
    # Base directory of the application
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # SQLite Database location inside workspace, with easy switch to MySQL
    # To use MySQL: set environment variable DATABASE_URL=mysql+pymysql://username:password@localhost/db_name
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(BASE_DIR, 'saree_factory.db')}"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Folder to store generated PDF invoices
    PDF_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'invoices')
    
    # Ensure PDF upload/invoice directory exists
    os.makedirs(PDF_FOLDER, exist_ok=True)
