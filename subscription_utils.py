import os
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, flash, request
import mercadopago

def init_mercadopago():
    """Initialize MercadoPago SDK"""
    access_token = os.environ.get('MERCADOPAGO_ACCESS_TOKEN')
    if not access_token:
        raise ValueError("MERCADOPAGO_ACCESS_TOKEN not found in environment variables")
    
    sdk = mercadopago.SDK(access_token)
    return sdk

def is_pro_user():
    """Check if current user has Pro access (either paid Pro or within trial period)"""
    if 'user_id' not in session:
        return False
    
    subscription_status = session.get('subscription_status', 'free')
    subscription_plan = session.get('subscription_plan', 'free')
    trial_end_date = session.get('trial_end_date')
    
    # Check if user has active Pro subscription
    if subscription_status == 'active' and subscription_plan == 'pro':
        return True
    
    # Check if user is within trial period
    if subscription_status == 'trial' and trial_end_date:
        try:
            if isinstance(trial_end_date, str):
                trial_end = datetime.fromisoformat(trial_end_date.replace('Z', '+00:00'))
            else:
                trial_end = trial_end_date
            
            if datetime.now() <= trial_end:
                return True
        except:
            pass
    
    return False

def require_pro(f):
    """Decorator to require Pro subscription or active trial"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_pro_user():
            flash('Esta funcionalidade requer um plano Pro. Assine agora ou aproveite seu teste gratuito!', 'warning')
            return redirect(url_for('subscription.plans'))
        return f(*args, **kwargs)
    return decorated_function

def require_login(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar esta página', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_trial_days_remaining():
    """Get number of days remaining in trial period"""
    if 'user_id' not in session:
        return 0
    
    trial_end_date = session.get('trial_end_date')
    if not trial_end_date:
        return 0
    
    try:
        if isinstance(trial_end_date, str):
            trial_end = datetime.fromisoformat(trial_end_date.replace('Z', '+00:00'))
        else:
            trial_end = trial_end_date
        
        days_remaining = (trial_end - datetime.now()).days
        return max(0, days_remaining)
    except:
        return 0

def create_subscription_preference(user_id, user_email):
    """Create MercadoPago preference for Pro subscription"""
    sdk = init_mercadopago()
    
    preference_data = {
        "items": [
            {
                "title": "CivilSaaS - Plano Pro",
                "description": "Assinatura mensal do plano Pro do CivilSaaS com todas as funcionalidades premium",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 49.90
            }
        ],
        "payer": {
            "email": user_email
        },
        "back_urls": {
            "success": f"{request.host_url}subscription/success",
            "failure": f"{request.host_url}subscription/failure",
            "pending": f"{request.host_url}subscription/pending"
        },
        "auto_return": "approved",
        "external_reference": str(user_id),
        "notification_url": f"{request.host_url}subscription/webhook"
    }
    
    preference_response = sdk.preference().create(preference_data)
    
    if preference_response["status"] == 201:
        return preference_response["response"]
    else:
        raise Exception(f"Error creating preference: {preference_response}")