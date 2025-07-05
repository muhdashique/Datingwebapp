# chat/views.py
from django.urls import path
from . import views

urlpatterns = [
    # Main chat interface
    path('', views.home, name='home'),
    
    # Chat functionality
    path('send-message/', views.send_message, name='send_message'),
    path('get-messages/<int:session_id>/', views.get_messages, name='get_messages'),
    path('new-chat/', views.new_chat, name='new_chat'),
    path('clear-chat/', views.clear_chat, name='clear_chat'),
    
    # Wikimedia API endpoints
    path('wikimedia-search/', views.wikimedia_search, name='wikimedia_search'),
    path('get-page-content/', views.get_page_content, name='get_page_content'),
    
    # User management
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.settings_view, name='settings'),
    
    # Chat history
    path('history/', views.chat_history, name='history'),
]
