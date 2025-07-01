# app/sockets.py - ALVIN Socket.IO Event Handlers
from datetime import datetime
import json
from flask import request, current_app
from flask_jwt_extended import decode_token, get_jwt_identity
from flask_socketio import emit, join_room, leave_room, disconnect
from app import socketio, db
from app.models import User, Project, ProjectCollaborator

# Store active users and their sessions
active_users = {}
typing_users = {}

def register_socket_events(socketio):
    """Register all Socket.IO event handlers"""
    
    @socketio.on('connect')
    def handle_connect(auth=None):
        """Handle client connection"""
        try:
            # Get user from token
            token = auth.get('token') if auth else None
            if not token:
                current_app.logger.warning('Socket connection without token')
                disconnect()
                return False
            
            # Verify user exists
            user = User.query.get(token)
            if not user:
                current_app.logger.warning(f'Socket connection with invalid user: {token}')
                disconnect()
                return False
            
            # Store user session
            session_id = request.sid
            active_users[session_id] = {
                'user_id': user.id,
                'username': user.username,
                'avatar_url': user.avatar_url,
                'connected_at': datetime.utcnow().isoformat(),
                'current_rooms': []
            }
            
            current_app.logger.info(f'User {user.username} connected (session: {session_id})')
            
            # Emit connection confirmation
            emit('connection_confirmed', {
                'user_id': user.id,
                'username': user.username,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            current_app.logger.error(f'Socket connection error: {e}')
            disconnect()
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        session_id = request.sid
        
        if session_id in active_users:
            user_data = active_users[session_id]
            username = user_data['username']
            
            # Leave all rooms and notify other users
            for room in user_data['current_rooms']:
                leave_room(room)
                emit('user_left', {
                    'user_id': user_data['user_id'],
                    'username': username,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=room)
            
            # Clean up typing status
            user_id = user_data['user_id']
            for room_id in list(typing_users.keys()):
                if user_id in typing_users[room_id]:
                    del typing_users[room_id][user_id]
                    emit('typing_status', {
                        'user_id': user_id,
                        'username': username,
                        'is_typing': False
                    }, room=room_id)
            
            # Remove from active users
            del active_users[session_id]
            current_app.logger.info(f'User {username} disconnected')
    
    @socketio.on('join_project')
    def handle_join_project(data):
        """Join a project room for real-time collaboration"""
        session_id = request.sid
        
        if session_id not in active_users:
            emit('error', {'message': 'User not authenticated'})
            return
        
        user_data = active_users[session_id]
        user_id = user_data['user_id']
        project_id = data.get('project_id')
        
        if not project_id:
            emit('error', {'message': 'Project ID required'})
            return
        
        # Verify user has access to project
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        if not project:
            # Check if user is a collaborator
            collaborator = ProjectCollaborator.query.filter_by(
                project_id=project_id, 
                user_id=user_id, 
                status='active'
            ).first()
            if not collaborator:
                emit('error', {'message': 'Access denied to project'})
                return
        
        # Join the project room
        room_name = f'project_{project_id}'
        join_room(room_name)
        
        # Add to user's rooms
        if room_name not in user_data['current_rooms']:
            user_data['current_rooms'].append(room_name)
        
        # Notify other users in the room
        emit('user_joined', {
            'user_id': user_id,
            'username': user_data['username'],
            'avatar_url': user_data.get('avatar_url'),
            'timestamp': datetime.utcnow().isoformat()
        }, room=room_name, include_self=False)
        
        # Send current room participants to new user
        room_users = []
        for sid, user_info in active_users.items():
            if room_name in user_info['current_rooms']:
                room_users.append({
                    'user_id': user_info['user_id'],
                    'username': user_info['username'],
                    'avatar_url': user_info.get('avatar_url'),
                    'connected_at': user_info['connected_at']
                })
        
        emit('room_users', {
            'room': room_name,
            'users': room_users
        })
        
        current_app.logger.info(f'User {user_data["username"]} joined project {project_id}')
    
    @socketio.on('leave_project')
    def handle_leave_project(data):
        """Leave a project room"""
        session_id = request.sid
        
        if session_id not in active_users:
            return
        
        user_data = active_users[session_id]
        project_id = data.get('project_id')
        
        if not project_id:
            return
        
        room_name = f'project_{project_id}'
        leave_room(room_name)
        
        # Remove from user's rooms
        if room_name in user_data['current_rooms']:
            user_data['current_rooms'].remove(room_name)
        
        # Notify other users
        emit('user_left', {
            'user_id': user_data['user_id'],
            'username': user_data['username'],
            'timestamp': datetime.utcnow().isoformat()
        }, room=room_name)
        
        current_app.logger.info(f'User {user_data["username"]} left project {project_id}')
    
    @socketio.on('scene_updated')
    def handle_scene_updated(data):
        """Broadcast scene updates to project collaborators"""
        session_id = request.sid
        
        if session_id not in active_users:
            return
        
        user_data = active_users[session_id]
        project_id = data.get('project_id')
        scene_data = data.get('scene_data')
        
        if not project_id or not scene_data:
            return
        
        room_name = f'project_{project_id}'
        
        # Broadcast to all users in the project room except sender
        emit('scene_updated', {
            'scene_data': scene_data,
            'updated_by': {
                'user_id': user_data['user_id'],
                'username': user_data['username']
            },
            'timestamp': datetime.utcnow().isoformat()
        }, room=room_name, include_self=False)
    
    @socketio.on('typing_status')
    def handle_typing_status(data):
        """Handle typing status updates"""
        session_id = request.sid
        
        if session_id not in active_users:
            return
        
        user_data = active_users[session_id]
        project_id = data.get('project_id')
        is_typing = data.get('is_typing', False)
        scene_id = data.get('scene_id')
        
        if not project_id:
            return
        
        room_name = f'project_{project_id}'
        user_id = user_data['user_id']
        
        # Initialize typing users for this room if needed
        if room_name not in typing_users:
            typing_users[room_name] = {}
        
        # Update typing status
        if is_typing:
            typing_users[room_name][user_id] = {
                'username': user_data['username'],
                'scene_id': scene_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            if user_id in typing_users[room_name]:
                del typing_users[room_name][user_id]
        
        # Broadcast typing status
        emit('typing_status', {
            'user_id': user_id,
            'username': user_data['username'],
            'is_typing': is_typing,
            'scene_id': scene_id,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room_name, include_self=False)
    
    @socketio.on('cursor_position')
    def handle_cursor_position(data):
        """Handle cursor position updates for collaborative editing"""
        session_id = request.sid
        
        if session_id not in active_users:
            return
        
        user_data = active_users[session_id]
        project_id = data.get('project_id')
        scene_id = data.get('scene_id')
        position = data.get('position')
        
        if not project_id or not scene_id or position is None:
            return
        
        room_name = f'project_{project_id}'
        
        # Broadcast cursor position
        emit('cursor_position', {
            'user_id': user_data['user_id'],
            'username': user_data['username'],
            'scene_id': scene_id,
            'position': position,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room_name, include_self=False)
    
    @socketio.on('comment_added')
    def handle_comment_added(data):
        """Handle new comment notifications"""
        session_id = request.sid
        
        if session_id not in active_users:
            return
        
        user_data = active_users[session_id]
        project_id = data.get('project_id')
        comment_data = data.get('comment_data')
        
        if not project_id or not comment_data:
            return
        
        room_name = f'project_{project_id}'
        
        # Broadcast new comment
        emit('comment_added', {
            'comment_data': comment_data,
            'added_by': {
                'user_id': user_data['user_id'],
                'username': user_data['username']
            },
            'timestamp': datetime.utcnow().isoformat()
        }, room=room_name, include_self=False)
    
    @socketio.on('get_room_status')
    def handle_get_room_status(data):
        """Get current status of a project room"""
        session_id = request.sid
        
        if session_id not in active_users:
            return
        
        project_id = data.get('project_id')
        if not project_id:
            return
        
        room_name = f'project_{project_id}'
        
        # Get current users in room
        room_users = []
        for sid, user_info in active_users.items():
            if room_name in user_info['current_rooms']:
                room_users.append({
                    'user_id': user_info['user_id'],
                    'username': user_info['username'],
                    'avatar_url': user_info.get('avatar_url'),
                    'connected_at': user_info['connected_at']
                })
        
        # Get current typing users
        current_typing = []
        if room_name in typing_users:
            for user_id, typing_data in typing_users[room_name].items():
                current_typing.append({
                    'user_id': user_id,
                    'username': typing_data['username'],
                    'scene_id': typing_data.get('scene_id'),
                    'timestamp': typing_data['timestamp']
                })
        
        emit('room_status', {
            'room': room_name,
            'users': room_users,
            'typing_users': current_typing,
            'timestamp': datetime.utcnow().isoformat()
        })

    return socketio