# chatbot/gemini_client.py
import google.generativeai as genai
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Google's Gemini API"""
    
    def __init__(self, api_key: str):
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.chat = None  # For multi-turn conversations
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def generate_response(self, prompt: str, chat_session=None) -> Optional[str]:
        """Generate a response from Gemini"""
        try:
            # If we have a chat session, use it for context
            if chat_session and hasattr(chat_session, 'id'):
                if self.chat is None:
                    self.chat = self.model.start_chat(history=[])
                
                response = self.chat.send_message(prompt)
                return response.text
            else:
                # For one-off responses
                response = self.model.generate_content(prompt)
                return response.text
        except Exception as e:
            logger.error(f"Error in Gemini generate_response: {e}")
            return None
    
    def reset_chat(self):
        """Reset the conversation history"""
        self.chat = None





 # chatbot/wikimedia_client.py
import requests
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class WikimediaClient:
    """Client for interacting with Wikimedia/Wikipedia APIs"""
    
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.session = requests.Session()
        logger.info("WikimediaClient initialized")
    
    def search_pages(self, query: str, limit: int = 5) -> List[Dict]:
        """Search Wikipedia pages"""
        try:
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'format': 'json',
                'srlimit': limit
            }
            
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return data.get('query', {}).get('search', [])
        except Exception as e:
            logger.error(f"Error in search_pages: {e}")
            return []
    
    def get_page_content(self, page_id: int) -> Optional[str]:
        """Get content of a Wikipedia page"""
        try:
            params = {
                'action': 'query',
                'prop': 'extracts',
                'pageids': page_id,
                'format': 'json',
                'explaintext': True,
                'exintro': True
            }
            
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            if str(page_id) in pages:
                return pages[str(page_id)].get('extract', 'No content available')
            
            return None
        except Exception as e:
            logger.error(f"Error in get_page_content: {e}")
            return None
    
    def get_random_page(self) -> Optional[Dict]:
        """Get a random Wikipedia page"""
        try:
            params = {
                'action': 'query',
                'generator': 'random',
                'grnnamespace': 0,
                'prop': 'extracts',
                'format': 'json',
                'explaintext': True,
                'exintro': True,
                'grnlimit': 1
            }
            
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            if pages:
                page_id = list(pages.keys())[0]
                return {
                    'title': pages[page_id].get('title', 'Untitled'),
                    'content': pages[page_id].get('extract', 'No content available'),
                    'pageid': page_id
                }
            
            return None
        except Exception as e:
            logger.error(f"Error in get_random_page: {e}")
            return None       
        



# chatbot/gemini_client.py
import google.generativeai as genai
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Google's Gemini API"""
    
    def __init__(self, api_key: str):
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.chat = None  # For multi-turn conversations
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def generate_response(self, prompt: str, chat_session=None) -> Optional[str]:
        """Generate a response from Gemini"""
        try:
            # Create a more conversational prompt
            enhanced_prompt = f"""You are a helpful and knowledgeable assistant. Please provide a helpful, informative, and conversational response to the following message:

{prompt}

Please be concise but informative, and maintain a friendly tone."""

            # If we have a chat session, use it for context
            if chat_session and hasattr(chat_session, 'id'):
                if self.chat is None:
                    self.chat = self.model.start_chat(history=[])
                
                response = self.chat.send_message(enhanced_prompt)
                return response.text
            else:
                # For one-off responses
                response = self.model.generate_content(enhanced_prompt)
                return response.text
                
        except Exception as e:
            logger.error(f"Error in Gemini generate_response: {e}")
            return None
    
    def reset_chat(self):
        """Reset the conversation history"""
        self.chat = None
        logger.info("Gemini chat session reset")
    
    def get_chat_history(self):
        """Get current chat history if available"""
        if self.chat and hasattr(self.chat, 'history'):
            return self.chat.history
        return []        