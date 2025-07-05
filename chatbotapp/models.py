# chatbot/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class ChatSession(models.Model):
    """Model to store chat sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_name = models.CharField(max_length=100, default="New Chat")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat {self.session_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def message_count(self):
        return self.messages.count()

class Message(models.Model):
    """Model to store individual messages"""
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('system', 'System'),
    ]
    
    chat_session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    # Optional fields for advanced features
    metadata = models.JSONField(default=dict, blank=True)  # Store additional data like response time, confidence, etc.
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

class BotPersonality(models.Model):
    """Model to store different bot personalities/configurations"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    system_prompt = models.TextField(help_text="System prompt that defines bot behavior")
    greeting_message = models.TextField(default="Hello! How can I help you today?")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name

class UserPreferences(models.Model):
    """Model to store user preferences for the chatbot"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_bot_personality = models.ForeignKey(BotPersonality, on_delete=models.SET_NULL, null=True, blank=True)
    theme = models.CharField(max_length=20, choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ], default='light')
    notifications_enabled = models.BooleanField(default=True)
    language = models.CharField(max_length=10, default='en')
    
    def __str__(self):
        return f"{self.user.username}'s preferences"

class ChatbotAnalytics(models.Model):
    """Model to store analytics data"""
    date = models.DateField(default=timezone.now)
    total_messages = models.IntegerField(default=0)
    total_sessions = models.IntegerField(default=0)
    unique_users = models.IntegerField(default=0)
    avg_response_time = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.date}"