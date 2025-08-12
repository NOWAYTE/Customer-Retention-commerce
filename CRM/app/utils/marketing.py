"""
Marketing automation utilities for triggering campaigns and webhooks.
"""
import json
import requests
from flask import current_app
from datetime import datetime
import time

class MarketingAutomationError(Exception):
    """Custom exception for marketing automation errors"""
    pass

def trigger_campaign(customer_data, risk_level, probability):
    """
    Trigger a marketing campaign based on customer risk level.
    
    Args:
        customer_data (dict): Customer data including features
        risk_level (str): 'high', 'medium', or 'low'
        probability (float): The churn probability (0.0 to 1.0)
        
    Returns:
        dict: Response from the marketing system
        
    Raises:
        MarketingAutomationError: If the webhook fails after retries
    """
    if not current_app.config.get('MARKETING_WEBHOOK_ENABLED', False):
        current_app.logger.info("Marketing webhook is disabled")
        return None
        
    webhook_url = current_app.config.get('MARKETING_WEBHOOK_URL')
    if not webhook_url:
        current_app.logger.warning("No marketing webhook URL configured")
        return None
        
    # Get campaign ID based on risk level
    campaign_id = current_app.config['CAMPAIGN_IDS'].get(f"{risk_level}_risk")
    if not campaign_id:
        current_app.logger.warning(f"No campaign ID configured for risk level: {risk_level}")
        return None
    
    # Prepare the payload
    payload = {
        'event': 'customer_risk_alert',
        'timestamp': datetime.utcnow().isoformat(),
        'customer': {
            'id': customer_data.get('customer_id', ''),
            'email': customer_data.get('email', ''),
            'risk_level': risk_level,
            'churn_probability': probability,
            'features': customer_data
        },
        'campaign': {
            'id': campaign_id,
            'trigger': 'churn_prediction',
            'priority': risk_level.upper()
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'CustomerRetentionCRM/1.0',
        'X-Request-ID': f"crm_{datetime.utcnow().timestamp()}"
    }
    
    # Add any additional headers from config
    if current_app.config.get('MARKETING_WEBHOOK_HEADERS'):
        headers.update(current_app.config['MARKETING_WEBHOOK_HEADERS'])
    
    max_retries = current_app.config.get('MARKETING_WEBHOOK_RETRIES', 3)
    timeout = current_app.config.get('MARKETING_WEBHOOK_TIMEOUT', 5)
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                webhook_url,
                data=json.dumps(payload),
                headers=headers,
                timeout=timeout
            )
            
            response.raise_for_status()
            
            current_app.logger.info(
                f"Successfully triggered {risk_level} risk campaign "
                f"for customer {customer_data.get('email')}"
            )
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            current_app.logger.warning(
                f"Attempt {attempt + 1}/{max_retries} failed: {last_error}"
            )
            
            if attempt < max_retries - 1:  # Don't sleep on the last attempt
                time.sleep(1 * (attempt + 1))  # Exponential backoff
    
    # If we get here, all retries failed
    error_msg = f"Failed to trigger marketing campaign after {max_retries} attempts: {last_error}"
    current_app.logger.error(error_msg)
    raise MarketingAutomationError(error_msg)

def trigger_campaign_by_risk(customer_data, probability):
    """
    Trigger the appropriate campaign based on risk probability.
    
    Args:
        customer_data (dict): Customer data including features
        probability (float): Churn probability (0.0 to 1.0)
        
    Returns:
        dict: Response from the marketing system or None if no action was taken
    """
    if probability >= current_app.config.get('RISK_THRESHOLD_HIGH', 0.7):
        risk_level = 'high'
    elif probability >= current_app.config.get('RISK_THRESHOLD_MEDIUM', 0.4):
        risk_level = 'medium'
    else:
        risk_level = 'low'
    
    try:
        return trigger_campaign(customer_data, risk_level, probability)
    except MarketingAutomationError as e:
        current_app.logger.error(f"Marketing automation error: {str(e)}")
        # Don't fail the entire prediction if marketing automation fails
        return None
