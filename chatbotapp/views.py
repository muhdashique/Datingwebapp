# chatbot/views.py (Updated with Wikimedia integration)
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
import json
import random
import time
import logging
from .models import ChatSession, Message, BotPersonality, UserPreferences
from .bot_logic import EnhancedChatBot
from .gemini_client import GeminiClient


# Initialize the enhanced chatbot
chatbot = EnhancedChatBot()
logger = logging.getLogger(__name__)

def home(request):
    """Main chat interface"""
    # Get or create a chat session
    if request.user.is_authenticated:
        chat_session, created = ChatSession.objects.get_or_create(
            user=request.user,
            is_active=True,
            defaults={'session_name': f'Chat {timezone.now().strftime("%Y-%m-%d %H:%M")}'}
        )
    else:
        # For anonymous users, use session
        session_id = request.session.get('chat_session_id')
        if session_id:
            try:
                chat_session = ChatSession.objects.get(id=session_id, user=None)
            except ChatSession.DoesNotExist:
                chat_session = ChatSession.objects.create(session_name="Anonymous Chat")
                request.session['chat_session_id'] = str(chat_session.id)
        else:
            chat_session = ChatSession.objects.create(session_name="Anonymous Chat")
            request.session['chat_session_id'] = str(chat_session.id)
    
    # Get recent messages
    messages_list = chat_session.messages.all()[:50]  # Last 50 messages
    
    # Get available bot personalities
    bot_personalities = BotPersonality.objects.filter(is_active=True)
    
    context = {
        'chat_session': chat_session,
        'messages': messages_list,
        'bot_personalities': bot_personalities,
    }
    
    return render(request, 'chat.html', context)
# In your views.py, update the send_message view
@csrf_exempt
def send_message(request):
    """Handle sending messages with Gemini integration"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message_content = data.get('message', '').strip()
            session_id = data.get('session_id')
            
            if not message_content:
                return JsonResponse({'error': 'Empty message'}, status=400)
            
            # Get chat session
            if request.user.is_authenticated:
                chat_session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            else:
                chat_session = get_object_or_404(ChatSession, id=session_id, user=None)
            
            # Save user message
            user_message = Message.objects.create(
                chat_session=chat_session,
                message_type='user',
                content=message_content
            )
            
            # Generate bot response using enhanced chatbot
            start_time = time.time()
            try:
                bot_response_content = chatbot.get_response(message_content, chat_session)
            except Exception as e:
                logger.error(f"Error generating bot response: {e}")
                bot_response_content = "I apologize, but I encountered an error while processing your request. Please try again."
            
            response_time = time.time() - start_time
            
            # Save bot message
            bot_message = Message.objects.create(
                chat_session=chat_session,
                message_type='bot',
                content=bot_response_content,
                metadata={
                    'response_time': response_time,
                    'used_wikimedia': chatbot.should_use_wikimedia(message_content),
                    'used_gemini': True  # Indicate Gemini was used
                }
            )
            
            # Update chat session
            chat_session.updated_at = timezone.now()
            chat_session.save()
            
            return JsonResponse({
                'success': True,
                'user_message': {
                    'id': user_message.id,
                    'content': user_message.content,
                    'timestamp': user_message.timestamp.isoformat(),
                    'type': 'user'
                },
                'bot_message': {
                    'id': bot_message.id,
                    'content': bot_message.content,
                    'timestamp': bot_message.timestamp.isoformat(),
                    'type': 'bot'
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error in send_message: {e}")
            return JsonResponse({'error': 'An error occurred while processing your message'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)








@csrf_exempt
def new_chat(request):
    """Create a new chat session"""
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Deactivate current active session
            ChatSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
            
            # Create new session
            chat_session = ChatSession.objects.create(
                user=request.user,
                session_name=f'Chat {timezone.now().strftime("%Y-%m-%d %H:%M")}',
                is_active=True
            )
        else:
            # For anonymous users
            chat_session = ChatSession.objects.create(session_name="Anonymous Chat")
            request.session['chat_session_id'] = str(chat_session.id)
        
        # Reset the Gemini chat session if it exists
        if hasattr(chatbot, 'gemini') and chatbot.gemini:
            chatbot.gemini.reset_chat()
        
        return JsonResponse({
            'success': True,
            'session_id': chat_session.id,
            'redirect_url': '/'
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)