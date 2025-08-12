# app/config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, '../instance/app.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hour
    
    # Marketing Automation Settings
    MARKETING_WEBHOOK_URL = os.environ.get('MARKETING_WEBHOOK_URL', 'https://marketing.example.com/webhook')
    MARKETING_WEBHOOK_ENABLED = os.environ.get('MARKETING_WEBHOOK_ENABLED', 'true').lower() in ('true', '1', 't')
    MARKETING_WEBHOOK_TIMEOUT = int(os.environ.get('MARKETING_WEBHOOK_TIMEOUT', 5))  # seconds
    MARKETING_WEBHOOK_RETRIES = int(os.environ.get('MARKETING_WEBHOOK_RETRIES', 3))
    
    # Risk thresholds for marketing actions (0.0 to 1.0)
    RISK_THRESHOLD_HIGH = float(os.environ.get('RISK_THRESHOLD_HIGH', '0.7'))
    RISK_THRESHOLD_MEDIUM = float(os.environ.get('RISK_THRESHOLD_MEDIUM', '0.4'))
    
    # Campaign IDs for different risk levels
    CAMPAIGN_IDS = {
        'high_risk': os.environ.get('HIGH_RISK_CAMPAIGN_ID', 'high_retention_campaign'),
        'medium_risk': os.environ.get('MEDIUM_RISK_CAMPAIGN_ID', 'medium_retention_campaign'),
        'low_risk': os.environ.get('LOW_RISK_CAMPAIGN_ID', 'low_retention_campaign')
    }
