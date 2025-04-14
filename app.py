import html
from re import T
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import logging
import datetime
import uuid
from logging.handlers import RotatingFileHandler
from ytcm_youtube_chat_reader import YouTubeChatReader
from ytcm_openai_service import OpenAIService
from ytcm_consts import *

app = Flask(__name__)

ytcm_ai_needed = YTCM_APPLY_MODERATION or YTCM_QUESTIONS_ONLY or YTCM_RETRIEVE_MSG_AUTHOR_GENDER or YTCM_APPLY_SPELLING_CORRECTION

# Logger configuration
def setup_logger():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logger = logging.getLogger('chat_magnifier')
    logger.setLevel(logging.DEBUG if YTCM_DEBUG_MODE else logging.ERROR)
    
    # Handler for log file
    file_handler = RotatingFileHandler('logs/yt-chat-magnifier.log', maxBytes=10485760, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    logger.addHandler(file_handler)
    
    # Handler for console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

# Class to manage chat messages
class ytcm_ChatMessageCustom:
    def __init__(self, author, text, is_male=True):
        self.id = str(uuid.uuid4())
        self.author = author
        self.text = text
        self.datetime = datetime.datetime.now()
        self.is_male = is_male
        self.show = True

    def __str__(self):
        return f"[{self.author}] - {self.text}"

ytcm_last_live_chat_id = None

# List to store chat messages
ytcm_chat_messages = []

# Service instances
ytcm_youtube_chat_reader = None
ytcm_openai_service = not ytcm_ai_needed

def ytcm_find_message(message: ytcm_ChatMessageCustom) -> bool:
    global ytcm_chat_messages
    for msg in ytcm_chat_messages:
        if str(msg) == str(message):
            if YTCM_TRACE_MODE:
                logger.info(f"Message found in the list: {msg}")
            return True
    return False

# Loading configurations
def ytcm_load_config(config_file):
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading configuration file {config_file}: {str(e)}")
        return None

@app.route('/')
def ytcm_index():
    ytcm_connect(True)
    live_title = ytcm_youtube_chat_reader.get_live_title() if ytcm_youtube_chat_reader else '...'
    return render_template('ytcm_index.html', connected=ytcm_youtube_chat_reader is not None, polling_interval=YTCM_POLLING_INTERVAL_MS, live_title=live_title)

@app.route('/ytcm_connect', methods=['POST'])
def ytcm_connect(resume_only=False):
    global ytcm_youtube_chat_reader, ytcm_openai_service, ytcm_chat_messages
    
    try:
        # Loading configurations
        google_config = ytcm_load_config(YTCM_GOOGLE_CONFIG_FILE)
        google_config['redirect_uri'] = request.url_root + 'ytcm_oauth2callback'
        openai_config = ytcm_load_config(YTCM_OPENAI_CONFIG_FILE)
        
        if not google_config or (ytcm_ai_needed and (not openai_config)):
            return jsonify({'success': False, 'error': 'Error loading configurations'})
        
        # Service initialization
        ytcm_youtube_chat_reader = YouTubeChatReader(google_config)

        if ytcm_ai_needed:
            ytcm_openai_service = OpenAIService(openai_config['api_key'])
        
        # Connection to YouTube
        success = ytcm_youtube_chat_reader.connect(resume_only)
        
        if success:
        
            if success == 'resumed':
                if YTCM_TRACE_MODE:
                    logger.info("YouTube connection resumed")
            else:
                if YTCM_TRACE_MODE:
                    logger.info("YouTube connection initialized")
                # Clear messages
                ytcm_chat_messages = []

            return jsonify({'success': True})
        else:
            if YTCM_DEBUG_MODE:
                logger.error("Error connecting to YouTube")
            ytcm_disconnect()
            return jsonify({'success': False, 'error': 'Error connecting to YouTube'})
    
    except Exception as e:
        if YTCM_DEBUG_MODE:
            logger.error(f"Error during connection: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/ytcm_oauth2callback')
def ytcm_oauth2callback():
    # This route is necessary to handle Google's OAuth2 authentication callback
    # The authentication flow is managed internally by InstalledAppFlow in ytcm_youtube_chat_reader.py
    # This route serves only as a return point after authentication
    return redirect(url_for('index'))

@app.route('/ytcm_disconnect', methods=['POST'])
def ytcm_disconnect():
    global ytcm_youtube_chat_reader, ytcm_openai_service, ytcm_chat_messages
    
    try:
        if ytcm_youtube_chat_reader:
            ytcm_youtube_chat_reader.disconnect()
            ytcm_youtube_chat_reader = None
        
        if ytcm_openai_service:
            ytcm_openai_service = not ytcm_ai_needed
        
        # Clear messages
        ytcm_chat_messages = []
        
        if YTCM_TRACE_MODE:
            logger.info("YouTube disconnection successful")
        
        return jsonify({'success': True})
    
    except Exception as e:
        if YTCM_DEBUG_MODE:
            logger.error(f"Error during disconnection: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/ytcm_toggle_message_visibility', methods=['POST'])
def ytcm_toggle_message_visibility():
    global ytcm_chat_messages
    
    try:
        # Get message ID and new show value from request
        data = request.get_json()
        message_id = data.get('id')
        show_value = data.get('show', True)
        
        if not message_id:
            return jsonify({'success': False, 'error': 'Message ID is required'})
        
        # Find the message with the given ID
        message_found = False
        for msg in ytcm_chat_messages:
            if msg.id == message_id:
                msg.show = show_value
                message_found = True
                if YTCM_TRACE_MODE:
                    logger.info(f"Message visibility changed: {msg.id} - show: {show_value}")
                break
        
        if not message_found:
            return jsonify({'success': False, 'error': 'Message not found'})
        
        return jsonify({'success': True})
    
    except Exception as e:
        if YTCM_DEBUG_MODE:
            logger.error(f"Error toggling message visibility: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/ytcm_get_messages')
def ytcm_get_messages():
    global ytcm_youtube_chat_reader, ytcm_openai_service, ytcm_chat_messages, ytcm_last_live_chat_id
    
    try:
        if not ytcm_youtube_chat_reader or not ytcm_openai_service:
            return jsonify({'success': False, 'error': 'Not connected to YouTube'})
        
        # Reading new messages from YouTube chat
        new_messages = ytcm_youtube_chat_reader.get_new_messages()
        if new_messages == False:
            ytcm_chat_messages = []
            return jsonify({'success': True, 'messages': [], 'error': 'No live stream found on the channel'})
            
        live_chat_id = ytcm_youtube_chat_reader.live_chat_id
        if live_chat_id != ytcm_last_live_chat_id:
            ytcm_last_live_chat_id = live_chat_id
            ytcm_chat_messages = []
            if YTCM_TRACE_MODE:
                logger.info(f"Live chat ID changed: {live_chat_id}")
                
        for msg in new_messages:
            # Verify that the message has at least 5 words
            words = msg['text'].split()
            if len(words) >= YTCM_MIN_MESSAGE_WORDS:
                if YTCM_TRACE_MODE:
                    logger.info(f"New message received: {msg['author']} - {msg['text']}")
                
                # Verify if the message is a question via OpenAI
                is_question = (not YTCM_QUESTIONS_ONLY) or ytcm_openai_service.is_question(msg['text'])
                
                if is_question and ((not YTCM_APPLY_MODERATION) or ytcm_openai_service.is_appropriate(msg['text'])):
                    msg_text = msg['text']
                    if YTCM_APPLY_SPELLING_CORRECTION:
                        # Correct spelling and improve text form while preserving special placeholders
                        msg_text = ytcm_openai_service.correct_text(msg_text)
                    # Create a new custom message
                    chat_msg = ytcm_ChatMessageCustom(msg['author'], msg_text, (not YTCM_RETRIEVE_MSG_AUTHOR_GENDER) or ytcm_openai_service.is_male_username(msg['author']))
                    if not ytcm_find_message(chat_msg):
                        ytcm_chat_messages.append(chat_msg)
                        if YTCM_TRACE_MODE:
                            logger.info(f"Message added to the list: {chat_msg}")
        
        # Format messages for the response
        formatted_messages = [{
            'id': msg.id,
            'author': msg.author,
            'text': msg.text,
            'datetime': msg.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'is_male': msg.is_male,
            'show': msg.show
        } for msg in ytcm_chat_messages]
        
        return jsonify({'success': True, 'messages': formatted_messages})
    
    except Exception as e:
        if YTCM_DEBUG_MODE:
            logger.error(f"Error reading messages: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Create necessary directories
    if not os.path.exists('config'):
        os.makedirs('config')
    
    # Check if configuration files exist
    if not os.path.exists(YTCM_GOOGLE_CONFIG_FILE):
        with open(YTCM_GOOGLE_CONFIG_FILE, 'w') as f:
            json.dump({
                "api_key": "YOUR_GOOGLE_API_KEY",
                "client_id": "YOUR_CLIENT_ID",
                "client_secret": "YOUR_CLIENT_SECRET"
            }, f, indent=4)
    
    if not os.path.exists(YTCM_OPENAI_CONFIG_FILE):
        with open(YTCM_OPENAI_CONFIG_FILE, 'w') as f:
            json.dump({
                "api_key": "YOUR_OPENAI_API_KEY"
            }, f, indent=4)

    # Start the application
    app.run(debug=YTCM_DEBUG_MODE)