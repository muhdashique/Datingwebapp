# chatbot/bot_logic.py
import logging
import random
import os
from .gemini_client import GeminiClient
from .wikimedia_client import WikimediaClient

logger = logging.getLogger(__name__)

class EnhancedChatBot:
    def __init__(self):
        # Initialize WikimediaClient
        try:
            self.wikimedia = WikimediaClient()
            logger.info("WikimediaClient initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WikimediaClient: {e}")
            self.wikimedia = None
            
        # Initialize GeminiClient with API key from environment variable
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            
            self.gemini = GeminiClient(api_key=api_key)
            logger.info("GeminiClient initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GeminiClient: {e}")
            self.gemini = None
            
        # Keywords that trigger Wikimedia search
        self.search_keywords = [
            'what is', 'who is', 'tell me about', 'search for',
            'find information', 'wikipedia', 'wiki', 'explain',
            'definition of', 'meaning of', 'about'
        ]
    
    def should_use_wikimedia(self, message: str) -> bool:
        """Determine if the message should be handled by Wikimedia"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.search_keywords)
    
    def extract_search_term(self, message: str) -> str:
        """Extract the search term from the message"""
        message_lower = message.lower()
        for keyword in self.search_keywords:
            if keyword in message_lower:
                # Find the position after the keyword and extract the remaining text
                start_pos = message_lower.find(keyword) + len(keyword)
                search_term = message[start_pos:].strip()
                # Remove common question words and punctuation
                search_term = search_term.lstrip('?.,!').strip()
                return search_term
        return message.strip()
    
    def get_detailed_info(self, search_term: str) -> str:
        """Get detailed information from Wikimedia"""
        if not self.wikimedia:
            return "Couldn't find detailed information (Wikimedia client unavailable)"
        
        # Try to get page summary first
        page_summary = self.wikimedia.get_page_summary(search_term)
        if page_summary and page_summary.get('extract'):
            title = page_summary.get('title', search_term)
            content = page_summary.get('extract', '')
            url = page_summary.get('url', '')
            
            # Limit content length for better readability
            if len(content) > 1500:
                content = content[:1500] + "..."
            
            response = f"**{title}**\n\n{content}"
            if url:
                response += f"\n\n[Read more on Wikipedia]({url})"
            return response
        
        # Fallback to search if direct page lookup fails
        search_results = self.wikimedia.search_pages(search_term)
        if not search_results:
            return f"Couldn't find detailed information about '{search_term}'"
        
        # Get content from the first search result
        first_result = search_results[0]
        page_id = first_result.get('pageid')
        if page_id:
            content = self.wikimedia.get_page_content(page_id)
            if content:
                title = first_result.get('title', search_term)
                # Limit content length
                if len(content) > 1500:
                    content = content[:1500] + "..."
                return f"**{title}**\n\n{content}"
        
        return f"Couldn't find detailed information about '{search_term}'"
    
    def format_search_results(self, search_results: list) -> str:
        """Format search results for display"""
        if not search_results:
            return "No results found. Try being more specific or check your spelling."
        
        formatted = ["Here are some results I found:\n"]
        for i, result in enumerate(search_results[:5], 1):  # Limit to 5 results
            title = result.get('title', 'Untitled')
            snippet = result.get('snippet', '')
            # Clean up HTML tags from snippet
            import re
            snippet = re.sub(r'<[^>]+>', '', snippet) if snippet else ''
            if len(snippet) > 100:
                snippet = snippet[:100] + "..."
            
            formatted.append(f"**{i}. {title}**")
            if snippet:
                formatted.append(f"   {snippet}")
            formatted.append("")  # Empty line for spacing
        
        return "\n".join(formatted).strip()
    
    def generate_regular_response(self, message: str, chat_session=None) -> str:
        """Generate regular chatbot responses using Gemini when available"""
        try:
            # First try Gemini if available
            if self.gemini:
                gemini_response = self.gemini.generate_response(message, chat_session)
                if gemini_response:
                    return gemini_response
            
            # Fallback to basic responses if Gemini fails
            message_lower = message.lower()
            
            # Greeting responses
            if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
                greetings = [
                    "Hello! I can help you find information or just chat. What would you like to know?",
                    "Hi there! I'm here to help with your questions or provide information.",
                    "Hey! Feel free to ask me anything - I can search for information or just have a conversation."
                ]
                return random.choice(greetings)
            
            # Help responses
            if any(word in message_lower for word in ['help', 'what can you do', 'how do you work']):
                return """I can help you with:
• **Information search**: Ask "What is..." or "Tell me about..." anything
• **Wikipedia articles**: I can find and summarize Wikipedia content
• **General conversation**: Just chat with me about topics you're interested in
• **Random articles**: Say "random" to get a random Wikipedia article

Try asking me something!"""
            
            # Random article
            if 'random' in message_lower and ('article' in message_lower or 'wikipedia' in message_lower or len(message_lower.split()) <= 2):
                if self.wikimedia:
                    random_page = self.wikimedia.get_random_page()
                    if random_page:
                        title = random_page.get('title', 'Unknown')
                        content = random_page.get('content', 'No content available')
                        url = random_page.get('url', '')
                        
                        if len(content) > 1000:
                            content = content[:1000] + "..."
                        
                        response = f"**Random Article: {title}**\n\n{content}"
                        if url:
                            response += f"\n\n[Read more on Wikipedia]({url})"
                        return response
                return "Random article feature is currently unavailable."
            
            # Default responses for unclear messages
            default_responses = [
                "I'm not sure I understand. Could you be more specific?",
                "Could you rephrase that? I'd be happy to help!",
                "I'm here to help! Try asking me about something specific.",
                "Feel free to ask me questions or tell me what you'd like to know about."
            ]
            return random.choice(default_responses)
            
        except Exception as e:
            logger.error(f"Error in generate_regular_response: {e}")
            return "I'm here to help! Ask me anything."
    
    def get_response(self, message: str, chat_session=None) -> str:
        """Main method to generate bot response"""
        try:
            if not message or not message.strip():
                return "Please ask me something!"
            
            message = message.strip()
            
            # Check if we should use Wikimedia for information search
            if self.should_use_wikimedia(message):
                search_term = self.extract_search_term(message)
                
                if search_term and len(search_term) > 1:
                    # For specific "what is/who is/tell me about" queries, get detailed info
                    if any(phrase in message.lower() for phrase in ['what is', 'who is', 'tell me about']):
                        detailed_info = self.get_detailed_info(search_term)
                        if "couldn't find detailed information" not in detailed_info.lower():
                            return detailed_info
                    
                    # For other search queries, show search results
                    if self.wikimedia:
                        search_results = self.wikimedia.search_pages(search_term)
                        if search_results:
                            return self.format_search_results(search_results)
                        else:
                            return f"I couldn't find any information about '{search_term}'. Try rephrasing your question or checking the spelling."
            
            # For non-search queries, use Gemini or fallback responses
            return self.generate_regular_response(message, chat_session)
            
        except Exception as e:
            logger.error(f"Error in get_response: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again."