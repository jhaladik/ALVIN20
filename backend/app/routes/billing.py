# app/routes/billing.py - ALVIN Billing Routes
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from sqlalchemy import desc, func
from app import db
from app.models import User, BillingPlan, UserSubscription, TokenUsageLog

billing_bp = Blueprint('billing', __name__)

# Validation schemas
class SubscribeSchema(Schema):
    plan_id = fields.Int(required=True)
    payment_method_id = fields.Str(missing=None)  # For payment integration

class BuyTokensSchema(Schema):
    amount = fields.Int(required=True, validate=lambda x: x > 0 and x <= 100000)
    payment_method_id = fields.Str(missing=None)  # For payment integration

@billing_bp.route('/plans', methods=['GET'])
def get_billing_plans():
    """Get all available billing plans"""
    plans = BillingPlan.query.filter_by(is_active=True, is_public=True).all()
    
    return jsonify({
        'plans': [plan.to_dict() for plan in plans]
    }), 200

@billing_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_current_subscription():
    """Get current user's subscription details"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': 'The authenticated user was not found'
        }), 404
    
    # Get current subscription
    subscription = UserSubscription.query.filter_by(
        user_id=current_user_id,
        status='active'
    ).first()
    
    # Get current plan details
    current_plan = BillingPlan.query.filter_by(name=user.plan).first()
    
    subscription_data = {
        'user_plan': user.plan,
        'tokens_used': user.tokens_used,
        'tokens_limit': user.tokens_limit,
        'tokens_remaining': user.get_remaining_tokens(),
        'plan_details': current_plan.to_dict() if current_plan else None,
        'subscription': subscription.to_dict() if subscription else None
    }
    
    # Add usage statistics
    if subscription:
        # Get usage for current period
        period_start = subscription.current_period_start
        period_end = subscription.current_period_end
        
        period_usage = TokenUsageLog.query.filter(
            TokenUsageLog.user_id == current_user_id,
            TokenUsageLog.created_at >= period_start,
            TokenUsageLog.created_at <= period_end,
            TokenUsageLog.billable == True
        ).with_entities(func.sum(TokenUsageLog.total_cost)).scalar() or 0
        
        subscription_data['period_usage'] = {
            'tokens_used_this_period': period_usage,
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat(),
            'days_remaining': (period_end - datetime.utcnow()).days
        }
    
    return jsonify(subscription_data), 200

@billing_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe_to_plan():
    """Subscribe user to a billing plan"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': 'The authenticated user was not found'
        }), 404
    
    try:
        # Validate input
        schema = SubscribeSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    # Get the plan
    plan = BillingPlan.query.filter_by(
        id=data['plan_id'],
        is_active=True,
        is_public=True
    ).first()
    
    if not plan:
        return jsonify({
            'error': 'Plan not found',
            'message': 'The specified billing plan was not found'
        }), 404
    
    # Check if user already has an active subscription
    existing_subscription = UserSubscription.query.filter_by(
        user_id=current_user_id,
        status='active'
    ).first()
    
    if existing_subscription:
        return jsonify({
            'error': 'Already subscribed',
            'message': 'You already have an active subscription. Please cancel it first to change plans.'
        }), 400
    
    try:
        # In a real implementation, this would integrate with Stripe or another payment processor
        # For now, we'll simulate the subscription creation
        
        # Calculate period dates
        period_start = datetime.utcnow()
        period_end = period_start + timedelta(days=30)  # Monthly subscription
        
        # Create subscription
        subscription = UserSubscription(
            user_id=current_user_id,
            plan_id=plan.id,
            status='active',
            current_period_start=period_start,
            current_period_end=period_end,
            # In real implementation, add Stripe IDs:
            # stripe_subscription_id=stripe_subscription.id,
            # stripe_customer_id=stripe_customer.id
        )
        
        # Update user plan and token limit
        user.plan = plan.name
        user.tokens_limit = plan.monthly_token_limit
        # Reset tokens for new subscription
        user.tokens_used = 0
        
        db.session.add(subscription)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully subscribed to {plan.display_name}',
            'subscription': subscription.to_dict(),
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Subscription creation error: {str(e)}")
        return jsonify({
            'error': 'Subscription failed',
            'message': 'An error occurred while processing your subscription'
        }), 500

@billing_bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel user's current subscription"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': 'The authenticated user was not found'
        }), 404
    
    # Get current subscription
    subscription = UserSubscription.query.filter_by(
        user_id=current_user_id,
        status='active'
    ).first()
    
    if not subscription:
        return jsonify({
            'error': 'No active subscription',
            'message': 'You do not have an active subscription to cancel'
        }), 400
    
    try:
        # In a real implementation, cancel with Stripe
        # stripe.Subscription.delete(subscription.stripe_subscription_id)
        
        # Mark subscription as cancelled
        subscription.status = 'cancelled'
        
        # Downgrade user to free plan
        free_plan = BillingPlan.query.filter_by(name='free').first()
        if free_plan:
            user.plan = 'free'
            user.tokens_limit = free_plan.monthly_token_limit
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subscription cancelled successfully',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Subscription cancellation error: {str(e)}")
        return jsonify({
            'error': 'Cancellation failed',
            'message': 'An error occurred while cancelling your subscription'
        }), 500

@billing_bp.route('/buy-tokens', methods=['POST'])
@jwt_required()
def buy_tokens():
    """Purchase additional tokens"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': 'The authenticated user was not found'
        }), 404
    
    try:
        # Validate input
        schema = BuyTokensSchema()
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({
            'error': 'Validation error',
            'message': 'Please check your input',
            'details': err.messages
        }), 400
    
    token_amount = data['amount']
    
    # Calculate price (example: $0.001 per token)
    price_per_token_cents = 0.1  # $0.001 = 0.1 cents
    total_price_cents = int(token_amount * price_per_token_cents)
    
    try:
        # In a real implementation, process payment with Stripe
        # payment_intent = stripe.PaymentIntent.create(
        #     amount=total_price_cents,
        #     currency='usd',
        #     payment_method=data.get('payment_method_id'),
        #     confirm=True
        # )
        
        # For now, simulate successful payment
        # Add tokens to user's limit
        user.tokens_limit += token_amount
        
        # Log the token purchase (you'd create a TokenPurchase model for this)
        # token_purchase = TokenPurchase(
        #     user_id=current_user_id,
        #     tokens_purchased=token_amount,
        #     price_paid_cents=total_price_cents,
        #     payment_status='completed'
        # )
        # db.session.add(token_purchase)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully purchased {token_amount} tokens',
            'tokens_purchased': token_amount,
            'price_paid_cents': total_price_cents,
            'price_paid_dollars': total_price_cents / 100,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Token purchase error: {str(e)}")
        return jsonify({
            'error': 'Purchase failed',
            'message': 'An error occurred while processing your token purchase'
        }), 500

@billing_bp.route('/token-usage', methods=['GET'])
@jwt_required()
def get_token_usage():
    """Get token usage analytics for the user"""
    current_user_id = get_jwt_identity()
    
    # Query parameters
    period = request.args.get('period', 'month')  # day, week, month, year
    limit = min(request.args.get('limit', 30, type=int), 365)
    
    # Calculate date range
    now = datetime.utcnow()
    if period == 'day':
        start_date = now - timedelta(days=limit)
        date_format = '%Y-%m-%d'
    elif period == 'week':
        start_date = now - timedelta(weeks=limit)
        date_format = '%Y-%W'
    elif period == 'month':
        start_date = now - timedelta(days=limit * 30)
        date_format = '%Y-%m'
    else:  # year
        start_date = now - timedelta(days=limit * 365)
        date_format = '%Y'
    
    # Get usage data
    usage_query = db.session.query(
        func.date_trunc(period, TokenUsageLog.created_at).label('period'),
        func.sum(TokenUsageLog.total_cost).label('total_tokens'),
        func.count(TokenUsageLog.id).label('operation_count'),
        TokenUsageLog.operation_type
    ).filter(
        TokenUsageLog.user_id == current_user_id,
        TokenUsageLog.created_at >= start_date,
        TokenUsageLog.billable == True
    ).group_by(
        func.date_trunc(period, TokenUsageLog.created_at),
        TokenUsageLog.operation_type
    ).order_by(
        func.date_trunc(period, TokenUsageLog.created_at).desc()
    ).all()
    
    # Format data for charts
    usage_by_period = {}
    usage_by_operation = {}
    
    for row in usage_query:
        period_key = row.period.strftime(date_format)
        
        # Aggregate by period
        if period_key not in usage_by_period:
            usage_by_period[period_key] = {
                'period': period_key,
                'total_tokens': 0,
                'operation_count': 0
            }
        
        usage_by_period[period_key]['total_tokens'] += row.total_tokens or 0
        usage_by_period[period_key]['operation_count'] += row.operation_count or 0
        
        # Aggregate by operation type
        if row.operation_type not in usage_by_operation:
            usage_by_operation[row.operation_type] = {
                'operation_type': row.operation_type,
                'total_tokens': 0,
                'operation_count': 0
            }
        
        usage_by_operation[row.operation_type]['total_tokens'] += row.total_tokens or 0
        usage_by_operation[row.operation_type]['operation_count'] += row.operation_count or 0
    
    # Get total usage statistics
    total_stats = db.session.query(
        func.sum(TokenUsageLog.total_cost).label('total_tokens'),
        func.count(TokenUsageLog.id).label('total_operations'),
        func.avg(TokenUsageLog.total_cost).label('avg_tokens_per_operation')
    ).filter(
        TokenUsageLog.user_id == current_user_id,
        TokenUsageLog.billable == True
    ).first()
    
    # Get most expensive operations
    top_operations = db.session.query(
        TokenUsageLog.operation_type,
        func.sum(TokenUsageLog.total_cost).label('total_cost'),
        func.count(TokenUsageLog.id).label('count')
    ).filter(
        TokenUsageLog.user_id == current_user_id,
        TokenUsageLog.created_at >= start_date,
        TokenUsageLog.billable == True
    ).group_by(
        TokenUsageLog.operation_type
    ).order_by(
        func.sum(TokenUsageLog.total_cost).desc()
    ).limit(10).all()
    
    return jsonify({
        'period': period,
        'date_range': {
            'start': start_date.isoformat(),
            'end': now.isoformat()
        },
        'usage_by_period': list(usage_by_period.values()),
        'usage_by_operation': list(usage_by_operation.values()),
        'total_stats': {
            'total_tokens': total_stats.total_tokens or 0,
            'total_operations': total_stats.total_operations or 0,
            'avg_tokens_per_operation': float(total_stats.avg_tokens_per_operation or 0)
        },
        'top_operations': [{
            'operation_type': op.operation_type,
            'total_cost': op.total_cost,
            'count': op.count,
            'avg_cost': op.total_cost / op.count if op.count > 0 else 0
        } for op in top_operations]
    }), 200

@billing_bp.route('/usage-export', methods=['GET'])
@jwt_required()
def export_usage_data():
    """Export detailed token usage data"""
    current_user_id = get_jwt_identity()
    
    # Query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    format_type = request.args.get('format', 'json')  # json, csv
    
    # Build query
    query = TokenUsageLog.query.filter_by(
        user_id=current_user_id,
        billable=True
    )
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(TokenUsageLog.created_at >= start_dt)
        except ValueError:
            return jsonify({
                'error': 'Invalid start_date format',
                'message': 'Please use ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS'
            }), 400
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(TokenUsageLog.created_at <= end_dt)
        except ValueError:
            return jsonify({
                'error': 'Invalid end_date format',
                'message': 'Please use ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS'
            }), 400
    
    # Get usage logs
    usage_logs = query.order_by(TokenUsageLog.created_at.desc()).limit(10000).all()
    
    if format_type == 'csv':
        # For CSV export, you'd implement CSV generation here
        # For now, return JSON with CSV structure
        csv_data = []
        for log in usage_logs:
            csv_data.append({
                'Date': log.created_at.isoformat() if log.created_at else '',
                'Operation': log.operation_type,
                'Input Tokens': log.input_tokens or 0,
                'Output Tokens': log.output_tokens or 0,
                'Total Cost': log.total_cost,
                'AI Model': log.ai_model_used or '',
                'Response Time (ms)': log.response_time_ms or 0,
                'Project ID': log.project_id or '',
                'Scene ID': log.scene_id or ''
            })
        
        return jsonify({
            'format': 'csv',
            'data': csv_data,
            'total_records': len(csv_data)
        }), 200
    
    else:
        # JSON format
        return jsonify({
            'format': 'json',
            'usage_logs': [log.to_dict() for log in usage_logs],
            'total_records': len(usage_logs),
            'query_params': {
                'start_date': start_date,
                'end_date': end_date
            }
        }), 200

@billing_bp.route('/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get user's billing invoices (placeholder for Stripe integration)"""
    current_user_id = get_jwt_identity()
    
    # In a real implementation, this would fetch invoices from Stripe
    # For now, return placeholder data
    
    return jsonify({
        'invoices': [],
        'message': 'Invoice history will be available when payment processing is enabled'
    }), 200