import os
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from subscription_utils import init_mercadopago, is_pro_user, require_login, create_subscription_preference, get_trial_days_remaining

subscription_bp = Blueprint('subscription', __name__)

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

@subscription_bp.route('/plans')
@require_login
def plans():
    """Show subscription plans"""
    trial_days = get_trial_days_remaining()
    is_pro = is_pro_user()
    
    return render_template('subscription/plans.html', 
                         trial_days=trial_days, 
                         is_pro=is_pro)

@subscription_bp.route('/checkout')
@require_login
def checkout():
    """Create checkout session for Pro subscription"""
    try:
        user_id = session.get('user_id')
        
        # Get user email from database
        db = get_db()
        user = db.execute('SELECT email FROM users WHERE id = ?', (user_id,)).fetchone()
        
        if not user:
            flash('Usuário não encontrado', 'error')
            return redirect(url_for('subscription.plans'))
        
        # Create MercadoPago preference
        preference = create_subscription_preference(user_id, user['email'])
        
        # Redirect to MercadoPago checkout
        return redirect(preference['init_point'])
        
    except Exception as e:
        flash(f'Erro ao processar pagamento: {str(e)}', 'error')
        return redirect(url_for('subscription.plans'))

@subscription_bp.route('/success')
@require_login
def success():
    """Handle successful payment"""
    payment_id = request.args.get('payment_id')
    status = request.args.get('status')
    
    if status == 'approved':
        # Update user subscription status
        user_id = session.get('user_id')
        db = get_db()
        
        subscription_start = datetime.now()
        subscription_end = subscription_start + timedelta(days=30)  # Monthly subscription
        
        db.execute('''
            UPDATE users 
            SET subscription_plan = ?, 
                subscription_status = ?, 
                subscription_start_date = ?, 
                subscription_end_date = ?
            WHERE id = ?
        ''', ('pro', 'active', subscription_start, subscription_end, user_id))
        db.commit()
        
        # Update session
        session['subscription_plan'] = 'pro'
        session['subscription_status'] = 'active'
        
        flash('Pagamento aprovado! Agora você tem acesso total ao plano Pro!', 'success')
    else:
        flash('Pagamento pendente. Aguarde a confirmação.', 'warning')
    
    return redirect(url_for('dashboard.index'))

@subscription_bp.route('/failure')
@require_login
def failure():
    """Handle failed payment"""
    flash('Pagamento não foi aprovado. Tente novamente.', 'error')
    return redirect(url_for('subscription.plans'))

@subscription_bp.route('/pending')
@require_login
def pending():
    """Handle pending payment"""
    flash('Pagamento está pendente. Aguarde a confirmação.', 'warning')
    return redirect(url_for('dashboard.index'))

@subscription_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle MercadoPago webhook notifications"""
    try:
        data = request.get_json()
        
        if data.get('type') == 'payment':
            payment_id = data.get('data', {}).get('id')
            
            # Get payment details from MercadoPago
            sdk = init_mercadopago()
            payment_response = sdk.payment().get(payment_id)
            
            if payment_response['status'] == 200:
                payment = payment_response['response']
                external_reference = payment.get('external_reference')
                status = payment.get('status')
                
                if status == 'approved' and external_reference:
                    # Update user subscription
                    db = get_db()
                    subscription_start = datetime.now()
                    subscription_end = subscription_start + timedelta(days=30)
                    
                    db.execute('''
                        UPDATE users 
                        SET subscription_plan = ?, 
                            subscription_status = ?, 
                            subscription_start_date = ?, 
                            subscription_end_date = ?
                        WHERE id = ?
                    ''', ('pro', 'active', subscription_start, subscription_end, int(external_reference)))
                    db.commit()
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@subscription_bp.route('/status')
@require_login
def status():
    """Show current subscription status"""
    user_id = session.get('user_id')
    db = get_db()
    
    user = db.execute('''
        SELECT subscription_plan, subscription_status, trial_end_date, 
               subscription_start_date, subscription_end_date
        FROM users WHERE id = ?
    ''', (user_id,)).fetchone()
    
    trial_days = get_trial_days_remaining()
    is_pro = is_pro_user()
    
    return render_template('subscription/status.html', 
                         user=user, 
                         trial_days=trial_days, 
                         is_pro=is_pro)