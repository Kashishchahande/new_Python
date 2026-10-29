import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'digital-notice-board-secret-key-2026')
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notices.db')
    
    # Default Admin Credentials (can be overridden with environment variables)
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # Notice Categories
    CATEGORIES = [
        'Academic',
        'Examination',
        'Events',
        'Placement',
        'Administrative',
        'Urgent Notice',
        'Sports',
        'General'
    ]
    
    # Priority Levels
    PRIORITIES = ['Urgent', 'High', 'Normal', 'Low']
