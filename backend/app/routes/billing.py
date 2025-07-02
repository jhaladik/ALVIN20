# backend/app/routes/billing.py - SIMPLIFIED BILLING ROUTES
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

billing_bp = Blueprint('billing', __name__)

# Mock billing data
BILLING_PLANS = [
    {
        'id': 1,
        'name': 'free',
        'display_name': 'Free Plan',
        'price': 0,
        'currency': 'USD',
        'interval': 'month',
        'tokens_limit': 1000,
        'features': [
            'Basic writing tools',
            '1,000 AI tokens per month',
            'Up to 3 projects',
            'Community support'
        ],
        'is_popular': False,
        'is_active': True
    },
    {
        'id': 2,
        'name': 'pro',
        'display_name': 'Pro Plan',
        'price': 9.99,
        'currency': 'USD',
        'interval': 'month',
        'tokens_limit': 10000,
        'features': [
            'Advanced AI tools',
            '10,000 AI tokens per month',
            'Unlimited projects',
            'Advanced analytics',
            'Priority support',
            'Export features'
        ],
        'is_popular': True,
        'is_active': True
    },
    {
        'id': 3,
        'name': 'premium',
        'display_name': 'Premium Plan',
        'price': 19.99,
        'currency': 'USD',
        'interval': 'month',
        'tokens_limit': 50000,
        'features': [
            'All Pro features',
            '50,000 AI tokens per month',
            'Real-time collaboration',
            'Custom AI models',
            'API access',
            'White-label options',
            'Dedicated support'
        ],
        'is_popular': False,
        'is_active': True
    }
]

TOKEN_PACKAGES = [
    {
        'id': 1,
        'name': 'starter',
        'amount': 1000,
        'price': 2.99,
        'currency': 'USD',
        'description': '1,000 additional AI tokens'
    },
    {
        'id': 2,
        'name': 'boost',
        'amount': 5000,
        'price': 12.99,
        'currency': 'USD',
        'description': '5,000 additional AI tokens',
        'savings': '13% off'
    },
    {
        'id': 3,
        'name': 'power',
        'amount': 10000,
        'price': 24.99,
        'currency': 'USD',
        'description': '10,000 additional AI tokens',
        'savings': '17% off'
    }
]

@billing_bp.route('/plans', methods=['GET'])
def get_billing_plans():
    """Get all available billing plans"""
    return jsonify({
        'plans': BILLING_PLANS,
        'total_plans': len(BILLING_PLANS),
        'currency': 'USD'
    }), 200

@billing_bp.route('/token-packages', methods=['GET'])
def get_token_packages():
    """Get available token packages"""
    return jsonify({
        'packages': TOKEN_PACKAGES,
        'total_packages': len(TOKEN_PACKAGES),
        'currency': 'USD'
    }), 200

@billing_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_current_subscription():
    """Get current user's subscription details"""
    current_user_id = get_jwt_identity()
    
    # Mock subscription data
    subscription_data = {
        'user_id': current_user_id,
        'current_plan': 'free',
        'plan_details': BILLING_PLANS[0],  # Free plan
        'tokens_used': 150,
        'tokens_limit': 1000,
        'tokens_remaining': 850,
        'billing_cycle': 'monthly',
        'next_billing_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),
        'subscription_status': 'active',
        'auto_renewal': True,
        'usage_this_month': {
            'ai_operations': 25,
            'projects_created': 2,
            'scenes_generated': 8,
            'tokens_consumed': 150
        }
    }
    
    return jsonify(subscription_data), 200

@billing_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe_to_plan():
    """Subscribe to a billing plan"""
    current_user_id = get_jwt_identity()
    
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        payment_method = data.get('payment_method_id', 'demo_payment')
        
        if not plan_id:
            return jsonify({
                'error': 'Plan ID required',
                'message': 'Please specify a plan_id'
            }), 400
        
        # Find the plan
        plan = next((p for p in BILLING_PLANS if p['id'] == plan_id), None)
        if not plan:
            return jsonify({
                'error': 'Plan not found',
                'message': 'The specified plan does not exist'
            }), 404
        
        # Mock subscription creation
        subscription = {
            'id': f'sub_{current_user_id}_{plan_id}',
            'user_id': current_user_id,
            'plan_id': plan_id,
            'plan_name': plan['name'],
            'status': 'active',
            'created_at': datetime.utcnow().isoformat(),
            'current_period_start': datetime.utcnow().isoformat(),
            'current_period_end': (datetime.utcnow() + timedelta(days=30)).isoformat(),
            'tokens_limit': plan['tokens_limit'],
            'amount': plan['price'],
            'currency': plan['currency'],
            'interval': plan['interval']
        }
        
        return jsonify({
            'success': True,
            'message': f'Successfully subscribed to {plan["display_name"]}',
            'subscription': subscription,
            'plan': plan
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Subscription error: {str(e)}")
        return jsonify({
            'error': 'Subscription failed',
            'message': 'An error occurred while processing your subscription'
        }), 500

@billing_bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel current subscription"""
    current_user_id = get_jwt_identity()
    
    # Mock cancellation
    return jsonify({
        'success': True,
        'message': 'Subscription cancelled successfully',
        'cancellation_date': datetime.utcnow().isoformat(),
        'effective_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),
        'refund_amount': 0,
        'downgrade_plan': 'free'
    }), 200

@billing_bp.route('/buy-tokens', methods=['POST'])
@jwt_required()
def buy_tokens():
    """Purchase additional tokens"""
    current_user_id = get_jwt_identity()
    
    try:
        data = request.get_json()
        package_id = data.get('package_id')
        amount = data.get('amount', 1000)
        
        if package_id:
            # Find the package
            package = next((p for p in TOKEN_PACKAGES if p['id'] == package_id), None)
            if not package:
                return jsonify({
                    'error': 'Package not found',
                    'message': 'The specified token package does not exist'
                }), 404
            
            amount = package['amount']
            price = package['price']
        else:
            # Custom amount
            price = amount * 0.003  # $0.003 per token
        
        # Mock token purchase
        purchase = {
            'id': f'purchase_{current_user_id}_{int(datetime.now().timestamp())}',
            'user_id': current_user_id,
            'tokens_purchased': amount,
            'price_paid': price,
            'currency': 'USD',
            'purchase_date': datetime.utcnow().isoformat(),
            'tokens_added_to_account': True
        }
        
        return jsonify({
            'success': True,
            'message': f'Successfully purchased {amount:,} tokens',
            'purchase': purchase,
            'new_token_balance': 1000 + amount  # Mock current balance + new tokens
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Token purchase error: {str(e)}")
        return jsonify({
            'error': 'Purchase failed',
            'message': 'An error occurred while processing your token purchase'
        }), 500

@billing_bp.route('/token-usage', methods=['GET'])
@jwt_required()
def get_token_usage():
    """Get token usage history"""
    current_user_id = get_jwt_identity()
    period = request.args.get('period', 'month')  # week, month, year
    
    # Mock usage data
    if period == 'week':
        usage_data = [
            {'date': '2025-06-26', 'tokens_used': 45, 'operations': 8},
            {'date': '2025-06-27', 'tokens_used': 32, 'operations': 6},
            {'date': '2025-06-28', 'tokens_used': 28, 'operations': 5},
            {'date': '2025-06-29', 'tokens_used': 55, 'operations': 12},
            {'date': '2025-06-30', 'tokens_used': 41, 'operations': 9},
            {'date': '2025-07-01', 'tokens_used': 38, 'operations': 7},
            {'date': '2025-07-02', 'tokens_used': 22, 'operations': 4}
        ]
    elif period == 'month':
        usage_data = [
            {'date': '2025-06-01', 'tokens_used': 856, 'operations': 124},
            {'date': '2025-07-01', 'tokens_used': 261, 'operations': 51}
        ]
    else:  # year
        usage_data = [
            {'date': '2025-01', 'tokens_used': 2340, 'operations': 345},
            {'date': '2025-02', 'tokens_used': 1890, 'operations': 278},
            {'date': '2025-03', 'tokens_used': 2156, 'operations': 312},
            {'date': '2025-04', 'tokens_used': 1756, 'operations': 267},
            {'date': '2025-05', 'tokens_used': 2045, 'operations': 298},
            {'date': '2025-06', 'tokens_used': 856, 'operations': 124},
            {'date': '2025-07', 'tokens_used': 261, 'operations': 51}
        ]
    
    total_tokens = sum(item['tokens_used'] for item in usage_data)
    total_operations = sum(item['operations'] for item in usage_data)
    
    return jsonify({
        'usage_data': usage_data,
        'period': period,
        'summary': {
            'total_tokens_used': total_tokens,
            'total_operations': total_operations,
            'average_tokens_per_operation': round(total_tokens / total_operations, 2) if total_operations > 0 else 0,
            'current_balance': 850  # Mock remaining balance
        }
    }), 200

@billing_bp.route('/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get billing invoices"""
    current_user_id = get_jwt_identity()
    
    # Mock invoice data
    invoices = [
        {
            'id': f'inv_{current_user_id}_001',
            'date': '2025-06-01',
            'amount': 9.99,
            'currency': 'USD',
            'status': 'paid',
            'description': 'Pro Plan - Monthly Subscription',
            'download_url': '/api/billing/invoices/inv_001/download'
        }
    ]
    
    return jsonify({
        'invoices': invoices,
        'total_invoices': len(invoices)
    }), 200

@billing_bp.route('/payment-methods', methods=['GET'])
@jwt_required()
def get_payment_methods():
    """Get saved payment methods"""
    current_user_id = get_jwt_identity()
    
    # Mock payment methods
    payment_methods = [
        {
            'id': 'pm_demo',
            'type': 'card',
            'brand': 'visa',
            'last4': '4242',
            'exp_month': 12,
            'exp_year': 2026,
            'is_default': True
        }
    ]
    
    return jsonify({
        'payment_methods': payment_methods,
        'total_methods': len(payment_methods)
    }), 200

@billing_bp.route('/status', methods=['GET'])
def billing_status():
    """Billing system status"""
    return jsonify({
        'billing_system': 'operational',
        'payment_processor': 'demo_mode',
        'available_plans': len(BILLING_PLANS),
        'available_packages': len(TOKEN_PACKAGES),
        'currencies_supported': ['USD'],
        'message': 'Billing system ready (demo mode)'
    }), 200