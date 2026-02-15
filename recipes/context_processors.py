"""
Context processors for SmartChef
"""

from .db import get_user_by_id


def user_context(request):
    """Add user and notification data to all templates"""
    user = None
    notifications = []
    theme = 'light'
    language = 'en'
    
    user_id = request.session.get('user_id')
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            theme = user.get('theme', 'light')
            language = user.get('language', 'en')
    
    # Get notifications from session
    notifications = request.session.pop('notifications', [])
    
    return {
        'current_user': user,
        'theme': theme,
        'language': language,
        'notifications': notifications,
    }
