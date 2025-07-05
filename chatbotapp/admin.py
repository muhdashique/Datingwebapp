# chatbot/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import ChatSession, Message, BotPersonality, UserPreferences, ChatbotAnalytics

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_name', 'user', 'message_count', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['session_name', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'message_count']
    date_hierarchy = 'created_at'
    
    def message_count(self, obj):
        return obj.message_count
    message_count.short_description = 'Messages'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['timestamp']
    fields = ['message_type', 'content', 'timestamp', 'is_read']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat_session', 'message_type', 'content_preview', 'timestamp', 'is_read']
    list_filter = ['message_type', 'timestamp', 'is_read']
    search_fields = ['content', 'chat_session__session_name']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('chat_session')

@admin.register(BotPersonality)
class BotPersonalityAdmin(admin.ModelAdmin):
    list_display = ['name', 'description_preview', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    def description_preview(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_preview.short_description = 'Description Preview'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Bot Configuration', {
            'fields': ('system_prompt', 'greeting_message')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_bot_personality', 'theme', 'language', 'notifications_enabled']
    list_filter = ['theme', 'language', 'notifications_enabled', 'preferred_bot_personality']
    search_fields = ['user__username', 'user__email']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'preferred_bot_personality')

@admin.register(ChatbotAnalytics)
class ChatbotAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_messages', 'total_sessions', 'unique_users', 'avg_response_time']
    list_filter = ['date']
    readonly_fields = ['date']
    date_hierarchy = 'date'
    
    def has_add_permission(self, request):
        return False  # Analytics should be generated automatically
    
    def has_change_permission(self, request, obj=None):
        return False  # Analytics should not be manually changed

# Custom admin site configuration
admin.site.site_header = "Chatbot Administration"
admin.site.site_title = "Chatbot Admin"
admin.site.index_title = "Welcome to Chatbot Administration"