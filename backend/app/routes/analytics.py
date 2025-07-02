# app/routes/analytics.py - ALVIN Analytics Routes
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, func, and_, or_
from app import db
from app.models import User, Project, Scene, StoryObject, TokenUsageLog, Comment

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/recent-activity', methods=['GET'])
@jwt_required()
def get_recent_activity():
    """Get recent activity for dashboard"""
    try:
        current_user_id = get_jwt_identity()
        limit = request.args.get('limit', 10, type=int)
        
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'The authenticated user was not found'
            }), 404
        
        # Get recent projects
        recent_projects = Project.query.filter_by(
            user_id=current_user_id
        ).order_by(desc(Project.updated_at)).limit(limit).all()
        
        # Get recent scenes
        recent_scenes = db.session.query(Scene).join(
            Project, Scene.project_id == Project.id
        ).filter(
            Project.user_id == current_user_id
        ).order_by(desc(Scene.updated_at)).limit(limit).all()
        
        # Combine activities and sort by timestamp
        activities = []
        
        # Add project activities
        for project in recent_projects:
            activities.append({
                'id': f"project_{project.id}",
                'type': 'project_updated',
                'title': f'Updated "{project.title}"',
                'description': project.description[:100] + '...' if project.description and len(project.description) > 100 else (project.description or 'No description'),
                'timestamp': project.updated_at.isoformat(),
                'project_id': project.id,
                'metadata': {
                    'project_title': project.title,
                    'project_phase': project.current_phase,
                    'word_count': project.current_word_count or 0
                }
            })
        
        # Add scene activities
        for scene in recent_scenes:
            activities.append({
                'id': f"scene_{scene.id}",
                'type': 'scene_updated',
                'title': f'Updated scene "{scene.title}"',
                'description': scene.description[:100] + '...' if scene.description and len(scene.description) > 100 else (scene.description or 'No description'),
                'timestamp': scene.updated_at.isoformat(),
                'scene_id': scene.id,
                'project_id': scene.project_id,
                'metadata': {
                    'scene_title': scene.title,
                    'scene_type': scene.scene_type,
                    'word_count': scene.word_count or 0
                }
            })
        
        # Sort by timestamp (most recent first) and limit
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        activities = activities[:limit]
        
        return jsonify({
            'activities': activities,
            'total': len(activities),
            'limit': limit
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Recent activity error: {str(e)}")
        return jsonify({
            'error': 'Failed to load recent activity',
            'message': 'An error occurred while loading recent activity',
            'activities': [],
            'total': 0
        }), 500

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    """Get comprehensive dashboard analytics for the user"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'message': 'The authenticated user was not found'
        }), 404
    
    # Date ranges for analysis
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Project statistics
    total_projects = Project.query.filter_by(user_id=current_user_id).count()
    active_projects = Project.query.filter_by(user_id=current_user_id, status='active').count()
    completed_projects = Project.query.filter_by(user_id=current_user_id, status='completed').count()
    
    # Recent project activity
    recent_projects = Project.query.filter_by(
        user_id=current_user_id
    ).order_by(desc(Project.updated_at)).limit(5).all()
    
    # Word count statistics
    total_word_count = db.session.query(
        func.sum(Project.current_word_count)
    ).filter_by(user_id=current_user_id).scalar() or 0
    
    # Scene statistics
    total_scenes = db.session.query(func.count(Scene.id)).join(
        Project, Scene.project_id == Project.id
    ).filter(Project.user_id == current_user_id).scalar() or 0
    
    # Token usage statistics
    total_tokens_used = user.tokens_used
    tokens_this_week = db.session.query(
        func.sum(TokenUsageLog.total_cost)
    ).filter(
        TokenUsageLog.user_id == current_user_id,
        TokenUsageLog.created_at >= week_ago,
        TokenUsageLog.billable == True
    ).scalar() or 0
    
    tokens_this_month = db.session.query(
        func.sum(TokenUsageLog.total_cost)
    ).filter(
        TokenUsageLog.user_id == current_user_id,
        TokenUsageLog.created_at >= month_ago,
        TokenUsageLog.billable == True
    ).scalar() or 0
    
    # AI operation statistics
    ai_operations_this_week = TokenUsageLog.query.filter(
        TokenUsageLog.user_id == current_user_id,
        TokenUsageLog.created_at >= week_ago
    ).count()
    
    # Most used AI operations
    top_ai_operations = db.session.query(
        TokenUsageLog.operation_type,
        func.count(TokenUsageLog.id).label('count'),
        func.sum(TokenUsageLog.total_cost).label('total_cost')
    ).filter(
        TokenUsageLog.user_id == current_user_id,
        TokenUsageLog.created_at >= month_ago
    ).group_by(TokenUsageLog.operation_type).order_by(
        func.count(TokenUsageLog.id).desc()
    ).limit(5).all()
    
    # Writing productivity (words per day over the last 30 days)
    productivity_data = []
    for i in range(30):
        date = now - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        # Count scenes created and words written that day
        scenes_created = db.session.query(func.count(Scene.id)).join(
            Project, Scene.project_id == Project.id
        ).filter(
            Project.user_id == current_user_id,
            Scene.created_at >= day_start,
            Scene.created_at < day_end
        ).scalar() or 0
        
        words_written = db.session.query(func.sum(Scene.word_count)).join(
            Project, Scene.project_id == Project.id
        ).filter(
            Project.user_id == current_user_id,
            Scene.created_at >= day_start,
            Scene.created_at < day_end
        ).scalar() or 0
        
        productivity_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'scenes_created': scenes_created,
            'words_written': words_written
        })
    
    # Genre distribution
    genre_distribution = db.session.query(
        Project.genre,
        func.count(Project.id).label('count')
    ).filter_by(
        user_id=current_user_id
    ).group_by(Project.genre).all()
    
    # Project phase distribution
    phase_distribution = db.session.query(
        Project.current_phase,
        func.count(Project.id).label('count')
    ).filter_by(
        user_id=current_user_id
    ).group_by(Project.current_phase).all()
    
    return jsonify({
        'overview': {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'total_scenes': total_scenes,
            'total_word_count': total_word_count,
            'tokens_used': total_tokens_used,
            'tokens_remaining': user.get_remaining_tokens(),
            'tokens_limit': user.tokens_limit
        },
        'recent_activity': {
            'tokens_this_week': tokens_this_week,
            'tokens_this_month': tokens_this_month,
            'ai_operations_this_week': ai_operations_this_week,
            'recent_projects': [p.to_dict() for p in recent_projects]
        },
        'ai_usage': {
            'top_operations': [{
                'operation_type': op.operation_type,
                'count': op.count,
                'total_cost': op.total_cost,
                'avg_cost': op.total_cost / op.count if op.count > 0 else 0
            } for op in top_ai_operations]
        },
        'productivity': {
            'daily_activity': productivity_data[:7],  # Last 7 days
            'monthly_trend': productivity_data  # Last 30 days
        },
        'distributions': {
            'genres': [{
                'genre': genre or 'Unspecified',
                'count': count
            } for genre, count in genre_distribution],
            'phases': [{
                'phase': phase,
                'count': count
            } for phase, count in phase_distribution]
        }
    }), 200

@analytics_bp.route('/projects/<project_id>', methods=['GET'])
@jwt_required()
def get_project_analytics(project_id):
    """Get detailed analytics for a specific project"""
    current_user_id = get_jwt_identity()
    
    # Verify project access
    project = Project.query.filter_by(id=project_id, user_id=current_user_id).first()
    if not project:
        return jsonify({
            'error': 'Project not found',
            'message': 'The requested project was not found'
        }), 404
    
    # Date ranges
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Scene analytics
    total_scenes = Scene.query.filter_by(project_id=project_id).count()
    completed_scenes = Scene.query.filter_by(project_id=project_id, status='completed').count()
    draft_scenes = Scene.query.filter_by(project_id=project_id, status='draft').count()
    
    # Word count progression
    scenes_by_date = db.session.query(
        func.date(Scene.created_at).label('date'),
        func.sum(Scene.word_count).label('words_added'),
        func.count(Scene.id).label('scenes_added')
    ).filter(
        Scene.project_id == project_id,
        Scene.created_at >= month_ago
    ).group_by(func.date(Scene.created_at)).order_by(
        func.date(Scene.created_at)
    ).all()
    
    # Scene type distribution
    scene_type_distribution = db.session.query(
        Scene.scene_type,
        func.count(Scene.id).label('count'),
        func.avg(Scene.word_count).label('avg_words'),
        func.avg(Scene.emotional_intensity).label('avg_intensity')
    ).filter_by(project_id=project_id).group_by(Scene.scene_type).all()
    
    # Story objects analytics
    total_objects = StoryObject.query.filter_by(project_id=project_id, status='active').count()
    object_type_distribution = db.session.query(
        StoryObject.object_type,
        func.count(StoryObject.id).label('count')
    ).filter_by(
        project_id=project_id,
        status='active'
    ).group_by(StoryObject.object_type).all()
    
    # Character role distribution (for character objects)
    character_roles = db.session.query(
        StoryObject.character_role,
        func.count(StoryObject.id).label('count')
    ).filter_by(
        project_id=project_id,
        object_type='character',
        status='active'
    ).group_by(StoryObject.character_role).all()
    
    # AI usage for this project
    project_ai_usage = db.session.query(
        TokenUsageLog.operation_type,
        func.count(TokenUsageLog.id).label('count'),
        func.sum(TokenUsageLog.total_cost).label('total_cost'),
        func.avg(TokenUsageLog.response_time_ms).label('avg_response_time')
    ).filter_by(
        project_id=project_id,
        user_id=current_user_id
    ).group_by(TokenUsageLog.operation_type).all()
    
    # Comments and collaboration analytics
    total_comments = Comment.query.filter_by(project_id=project_id).count()
    recent_comments = Comment.query.filter(
        Comment.project_id == project_id,
        Comment.created_at >= week_ago
    ).count()
    
    # Emotional intensity analysis
    intensity_analysis = db.session.query(
        func.avg(Scene.emotional_intensity).label('avg_intensity'),
        func.min(Scene.emotional_intensity).label('min_intensity'),
        func.max(Scene.emotional_intensity).label('max_intensity'),
        func.count(Scene.id).label('total_scenes')
    ).filter_by(project_id=project_id).first()
    
    # Writing velocity (words per scene creation session)
    writing_velocity = []
    scenes_ordered = Scene.query.filter_by(
        project_id=project_id
    ).order_by(Scene.created_at).all()
    
    if len(scenes_ordered) > 1:
        for i in range(1, len(scenes_ordered)):
            prev_scene = scenes_ordered[i-1]
            curr_scene = scenes_ordered[i]
            
            time_diff = (curr_scene.created_at - prev_scene.created_at).total_seconds() / 3600  # hours
            if time_diff > 0 and time_diff < 24:  # Same day writing sessions
                velocity = curr_scene.word_count / time_diff if time_diff > 0 else 0
                writing_velocity.append({
                    'date': curr_scene.created_at.strftime('%Y-%m-%d'),
                    'words_per_hour': velocity,
                    'session_duration_hours': time_diff,
                    'words_written': curr_scene.word_count
                })
    
    return jsonify({
        'project': project.to_dict(),
        'scene_analytics': {
            'total_scenes': total_scenes,
            'completed_scenes': completed_scenes,
            'draft_scenes': draft_scenes,
            'completion_rate': (completed_scenes / total_scenes * 100) if total_scenes > 0 else 0,
            'scene_types': [{
                'type': st.scene_type,
                'count': st.count,
                'avg_words': float(st.avg_words or 0),
                'avg_intensity': float(st.avg_intensity or 0)
            } for st in scene_type_distribution]
        },
        'word_count_progression': [{
            'date': progress.date.strftime('%Y-%m-%d'),
            'words_added': progress.words_added or 0,
            'scenes_added': progress.scenes_added or 0
        } for progress in scenes_by_date],
        'story_objects': {
            'total_objects': total_objects,
            'by_type': [{
                'type': ot.object_type,
                'count': ot.count
            } for ot in object_type_distribution],
            'character_roles': [{
                'role': cr.character_role or 'Unspecified',
                'count': cr.count
            } for cr in character_roles]
        },
        'ai_usage': [{
            'operation_type': ai.operation_type,
            'count': ai.count,
            'total_cost': ai.total_cost,
            'avg_cost': ai.total_cost / ai.count if ai.count > 0 else 0,
            'avg_response_time_ms': float(ai.avg_response_time or 0)
        } for ai in project_ai_usage],
        'collaboration': {
            'total_comments': total_comments,
            'recent_comments': recent_comments,
            'comments_per_scene': total_comments / total_scenes if total_scenes > 0 else 0
        },
        'emotional_analysis': {
            'avg_intensity': float(intensity_analysis.avg_intensity or 0),
            'min_intensity': float(intensity_analysis.min_intensity or 0),
            'max_intensity': float(intensity_analysis.max_intensity or 0),
            'intensity_range': float((intensity_analysis.max_intensity or 0) - (intensity_analysis.min_intensity or 0))
        },
        'writing_velocity': writing_velocity[-10:]  # Last 10 writing sessions
    }), 200

@analytics_bp.route('/writing-stats', methods=['GET'])
@jwt_required()
def get_writing_statistics():
    """Get comprehensive writing statistics and trends"""
    current_user_id = get_jwt_identity()
    
    # Query parameters
    period = request.args.get('period', 'month')  # week, month, quarter, year
    project_id = request.args.get('project_id')
    
    # Calculate date range
    now = datetime.utcnow()
    if period == 'week':
        start_date = now - timedelta(days=7)
        date_format = '%Y-%m-%d'
    elif period == 'month':
        start_date = now - timedelta(days=30)
        date_format = '%Y-%m-%d'
    elif period == 'quarter':
        start_date = now - timedelta(days=90)
        date_format = '%Y-%m-%d'
    else:  # year
        start_date = now - timedelta(days=365)
        date_format = '%Y-%m'
    
    # Base query
    base_query = db.session.query(Scene).join(
        Project, Scene.project_id == Project.id
    ).filter(
        Project.user_id == current_user_id,
        Scene.created_at >= start_date
    )
    
    # Filter by project if specified
    if project_id:
        base_query = base_query.filter(Scene.project_id == project_id)
    
    # Daily writing statistics
    daily_stats = db.session.query(
        func.date(Scene.created_at).label('date'),
        func.count(Scene.id).label('scenes_written'),
        func.sum(Scene.word_count).label('words_written'),
        func.avg(Scene.word_count).label('avg_words_per_scene'),
        func.avg(Scene.emotional_intensity).label('avg_emotional_intensity')
    ).select_from(base_query.subquery()).group_by(
        func.date(Scene.created_at)
    ).order_by(func.date(Scene.created_at)).all()
    
    # Writing streaks
    writing_days = [stat.date for stat in daily_stats]
    current_streak = 0
    longest_streak = 0
    streak_count = 0
    
    # Calculate streaks
    for i, day in enumerate(writing_days):
        if i == 0 or (day - writing_days[i-1]).days == 1:
            streak_count += 1
        else:
            longest_streak = max(longest_streak, streak_count)
            streak_count = 1
    
    # Check current streak
    if writing_days and (now.date() - writing_days[-1]).days <= 1:
        current_streak = streak_count
    
    longest_streak = max(longest_streak, streak_count)
    
    # Genre preferences over time
    genre_trends = db.session.query(
        Project.genre,
        func.date_trunc(period, Scene.created_at).label('period'),
        func.count(Scene.id).label('scene_count'),
        func.sum(Scene.word_count).label('word_count')
    ).join(Project, Scene.project_id == Project.id).filter(
        Project.user_id == current_user_id,
        Scene.created_at >= start_date
    ).group_by(
        Project.genre,
        func.date_trunc(period, Scene.created_at)
    ).all()
    
    # Writing time patterns (hour of day analysis)
    hourly_patterns = db.session.query(
        func.extract('hour', Scene.created_at).label('hour'),
        func.count(Scene.id).label('scenes_written'),
        func.avg(Scene.word_count).label('avg_words')
    ).join(Project, Scene.project_id == Project.id).filter(
        Project.user_id == current_user_id,
        Scene.created_at >= start_date
    ).group_by(func.extract('hour', Scene.created_at)).order_by(
        func.extract('hour', Scene.created_at)
    ).all()
    
    # Weekly patterns (day of week analysis)
    weekly_patterns = db.session.query(
        func.extract('dow', Scene.created_at).label('day_of_week'),
        func.count(Scene.id).label('scenes_written'),
        func.avg(Scene.word_count).label('avg_words')
    ).join(Project, Scene.project_id == Project.id).filter(
        Project.user_id == current_user_id,
        Scene.created_at >= start_date
    ).group_by(func.extract('dow', Scene.created_at)).order_by(
        func.extract('dow', Scene.created_at)
    ).all()
    
    # Goal tracking (example goals)
    goals = {
        'daily_word_target': 500,
        'weekly_scene_target': 3,
        'monthly_project_target': 1
    }
    
    # Calculate goal achievement
    total_words_this_period = sum([stat.words_written or 0 for stat in daily_stats])
    total_scenes_this_period = sum([stat.scenes_written or 0 for stat in daily_stats])
    
    days_in_period = (now - start_date).days + 1
    avg_words_per_day = total_words_this_period / days_in_period if days_in_period > 0 else 0
    avg_scenes_per_week = total_scenes_this_period / (days_in_period / 7) if days_in_period > 0 else 0
    
    return jsonify({
        'period': period,
        'date_range': {
            'start': start_date.isoformat(),
            'end': now.isoformat()
        },
        'daily_writing': [{
            'date': stat.date.strftime('%Y-%m-%d'),
            'scenes_written': stat.scenes_written or 0,
            'words_written': stat.words_written or 0,
            'avg_words_per_scene': float(stat.avg_words_per_scene or 0),
            'avg_emotional_intensity': float(stat.avg_emotional_intensity or 0)
        } for stat in daily_stats],
        'streaks': {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'total_writing_days': len(writing_days)
        },
        'totals': {
            'total_words': total_words_this_period,
            'total_scenes': total_scenes_this_period,
            'avg_words_per_day': avg_words_per_day,
            'avg_scenes_per_week': avg_scenes_per_week
        },
        'patterns': {
            'hourly': [{
                'hour': int(pattern.hour),
                'scenes_written': pattern.scenes_written or 0,
                'avg_words': float(pattern.avg_words or 0)
            } for pattern in hourly_patterns],
            'weekly': [{
                'day_of_week': int(pattern.day_of_week),
                'day_name': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][int(pattern.day_of_week)],
                'scenes_written': pattern.scenes_written or 0,
                'avg_words': float(pattern.avg_words or 0)
            } for pattern in weekly_patterns]
        },
        'goals': {
            'targets': goals,
            'achievement': {
                'daily_words': {
                    'target': goals['daily_word_target'],
                    'actual': avg_words_per_day,
                    'percentage': (avg_words_per_day / goals['daily_word_target'] * 100) if goals['daily_word_target'] > 0 else 0
                },
                'weekly_scenes': {
                    'target': goals['weekly_scene_target'],
                    'actual': avg_scenes_per_week,
                    'percentage': (avg_scenes_per_week / goals['weekly_scene_target'] * 100) if goals['weekly_scene_target'] > 0 else 0
                }
            }
        }
    }), 200

@analytics_bp.route('/export', methods=['GET'])
@jwt_required()
def export_analytics_data():
    """Export analytics data in various formats"""
    current_user_id = get_jwt_identity()
    
    # Query parameters
    data_type = request.args.get('type', 'overview')  # overview, projects, scenes, ai_usage
    format_type = request.args.get('format', 'json')  # json, csv
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Date filtering
    date_filter = []
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            date_filter.append(lambda model: model.created_at >= start_dt)
        except ValueError:
            return jsonify({
                'error': 'Invalid start_date format',
                'message': 'Please use ISO format: YYYY-MM-DD'
            }), 400
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            date_filter.append(lambda model: model.created_at <= end_dt)
        except ValueError:
            return jsonify({
                'error': 'Invalid end_date format',
                'message': 'Please use ISO format: YYYY-MM-DD'
            }), 400
    
    try:
        if data_type == 'projects':
            query = Project.query.filter_by(user_id=current_user_id)
            for filter_func in date_filter:
                query = query.filter(filter_func(Project))
            data = [project.to_dict(include_scenes=True, include_objects=True) for project in query.all()]
        
        elif data_type == 'scenes':
            query = db.session.query(Scene).join(
                Project, Scene.project_id == Project.id
            ).filter(Project.user_id == current_user_id)
            for filter_func in date_filter:
                query = query.filter(filter_func(Scene))
            data = [scene.to_dict() for scene in query.all()]
        
        elif data_type == 'ai_usage':
            query = TokenUsageLog.query.filter_by(user_id=current_user_id)
            for filter_func in date_filter:
                query = query.filter(filter_func(TokenUsageLog))
            data = [log.to_dict() for log in query.all()]
        
        else:  # overview
            # Compile overview statistics
            data = {
                'user_id': current_user_id,
                'export_date': datetime.utcnow().isoformat(),
                'projects': Project.query.filter_by(user_id=current_user_id).count(),
                'scenes': db.session.query(func.count(Scene.id)).join(
                    Project, Scene.project_id == Project.id
                ).filter(Project.user_id == current_user_id).scalar(),
                'total_words': db.session.query(func.sum(Project.current_word_count)).filter_by(
                    user_id=current_user_id
                ).scalar() or 0,
                'ai_operations': TokenUsageLog.query.filter_by(user_id=current_user_id).count(),
                'tokens_used': TokenUsageLog.query.filter_by(user_id=current_user_id).with_entities(
                    func.sum(TokenUsageLog.total_cost)
                ).scalar() or 0
            }
        
        return jsonify({
            'data_type': data_type,
            'format': format_type,
            'exported_at': datetime.utcnow().isoformat(),
            'record_count': len(data) if isinstance(data, list) else 1,
            'data': data
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Analytics export error: {str(e)}")
        return jsonify({
            'error': 'Export failed',
            'message': 'An error occurred while exporting analytics data'
        }), 500