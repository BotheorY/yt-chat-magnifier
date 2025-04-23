from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import logging
import datetime
import uuid
from logging.handlers import RotatingFileHandler
from ytcm_youtube_chat_reader import YouTubeChatReader
from ytcm_openai_service import OpenAIService
from ytcm_polly_service import PollyService
from ytcm_consts import *
from googleapiclient.discovery import build
from urllib.parse import urlparse
import hashlib

app = Flask(__name__)

ytcm_ai_needed = YTCM_APPLY_MODERATION or YTCM_QUESTIONS_ONLY or YTCM_RETRIEVE_MSG_AUTHOR_GENDER or YTCM_APPLY_SPELLING_CORRECTION

# Check if TTS service is enabled
ytcm_tts_enabled = bool(YTCM_MALE_TTS_VOICE or YTCM_FEMALE_TTS_VOICE)

# Logger configuration
def setup_logger():
    # Create logs directory if it doesn't exist
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs'))
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    logger = logging.getLogger('chat_magnifier')
    logger.setLevel(logging.DEBUG if YTCM_DEBUG_MODE else logging.ERROR)
    
    # Remove any existing handlers to avoid duplicates
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    
    try:
        # Handler for log file with error handling
        log_file_path = os.path.join(logs_dir, 'yt-chat-magnifier.log')
        file_handler = RotatingFileHandler(
            log_file_path, 
            maxBytes=10485760, 
            backupCount=10,
            delay=True  # Delay file opening until first log write
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        logger.addHandler(file_handler)
    except (OSError, IOError) as e:
        # Fall back to console-only logging if file handler fails
        print(f"Warning: Could not set up file logging: {str(e)}")
    
    # Handler for console (always add this as a fallback)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

def get_audio_file_dir_full_path(): 
    return os.path.abspath(os.path.join(os.path.dirname(__file__), YTCM_TTS_AUDIO_FILES_DIR))

audio_file_dir_full_path = get_audio_file_dir_full_path()

# Class to manage chat messages
class ytcm_ChatMessageCustom:
    def __init__(self, author, text, is_male=True, raw_text=None):
        self.author = author
        self.text = text
        self.datetime = datetime.datetime.now()
        self.is_male = is_male
        self.show = True
        self.raw_text = raw_text if raw_text else text
        self.id = hashlib.sha256(f"{author}|{self.raw_text}".encode()).hexdigest()

    def __str__(self):
        return f"[{self.author}] - {self.raw_text}"

ytcm_last_live_chat_id = None

# List to store chat messages
ytcm_chat_messages = []
ytcm_hidden_msg_ids: set = set()

# Service instances
ytcm_youtube_chat_reader = None
ytcm_openai_service = not ytcm_ai_needed
ytcm_polly_service = None

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

def ytcm_clear_audio_files():
    try:
        # Check if the directory exists
        if not os.path.exists(audio_file_dir_full_path):
            os.makedirs(audio_file_dir_full_path)
            return jsonify({'success': True, 'message': 'Directory was empty'})
        
        # Count the deleted files
        deleted_count = 0
        
        # Delete all .mp3 files in the directory
        for filename in os.listdir(audio_file_dir_full_path):
            if filename.endswith('.mp3'):
                file_path = os.path.join(audio_file_dir_full_path, filename)
                os.remove(file_path)
                deleted_count += 1
                if YTCM_TRACE_MODE:
                    logger.info(f"Deleted audio file: {filename}")
        
        if YTCM_TRACE_MODE:
            logger.info(f"Cleared {deleted_count} audio files from {audio_file_dir_full_path}")
        
        return jsonify({'success': True, 'message': f'Deleted {deleted_count} audio files'})
    
    except Exception as e:
        if YTCM_DEBUG_MODE:
            logger.error(f"Error clearing audio files: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/ytcm_check_audio_file')
def ytcm_check_audio_file():
    message_id = request.args.get('id')
    if not message_id:
        return jsonify({'exists': False, 'error': 'Message ID is required'})
    
    file_path = os.path.join(audio_file_dir_full_path, f"{message_id}.mp3")
    exists = os.path.exists(file_path)
    
    return jsonify({'exists': exists})

@app.route('/ytcm_generate_audio', methods=['POST'])
def ytcm_generate_audio():
    global ytcm_polly_service
    
    if not ytcm_tts_enabled:
        return jsonify({'success': False, 'error': 'TTS service is not enabled'})
    
    if not ytcm_polly_service or not ytcm_polly_service.is_available():
        return jsonify({'success': False, 'error': 'AWS Polly service not available'})
    
    try:
        data = request.get_json()
        message_id = data.get('id')
        text = data.get('text')
        is_male = data.get('is_male', True)
        
        if not message_id or not text:
            return jsonify({'success': False, 'error': 'Message ID and text are required'})
        
        # Generate the audio file
        success = ytcm_polly_service.generate_audio(text, message_id, is_male)
        
        return jsonify({'success': success})
    
    except Exception as e:
        if YTCM_DEBUG_MODE:
            logger.error(f"Error generating audio: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/')
def ytcm_index():
    ytcm_connect(True)
    live_title = ytcm_youtube_chat_reader.get_live_title() if ytcm_youtube_chat_reader else '...'
    channel_name = ytcm_youtube_chat_reader.get_channel_name() if ytcm_youtube_chat_reader else '...'
    return render_template('ytcm_index.html', connected=ytcm_youtube_chat_reader is not None, polling_interval=YTCM_POLLING_INTERVAL_MS, live_title=live_title, channel_name=channel_name, tts_enabled=ytcm_tts_enabled, tts_audio_files_dir=YTCM_TTS_AUDIO_FILES_DIR, layout_style=YTCM_LAYOUT_STYLE)

@app.route('/ytcm_connect', methods=['POST'])
def ytcm_connect(resume_only=False):
    global ytcm_youtube_chat_reader, ytcm_openai_service, ytcm_polly_service, ytcm_chat_messages
    
    try:
        # Loading configurations
        google_config = ytcm_load_config(YTCM_GOOGLE_CONFIG_FILE)
        openai_config = ytcm_load_config(YTCM_OPENAI_CONFIG_FILE)
        
        if not google_config or (ytcm_ai_needed and (not openai_config)):
            return jsonify({'success': False, 'error': 'Error loading configurations'})
        
        # Initialize AWS Polly service if enabled
        if ytcm_tts_enabled and not ytcm_polly_service:
            ytcm_polly_service = PollyService(YTCM_POLLY_CONFIG_FILE)
        
        # Service initialization
        ytcm_youtube_chat_reader = YouTubeChatReader()

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
                    logger.info("YouTube connection in progress...")
                # Clear messages
                ytcm_chat_messages = []
                ytcm_clear_audio_files()
                if isinstance(success, str):
                    res = urlparse(success)
                    if all([res.scheme, res.netloc]) and (res.scheme == 'https') and ('.' in res.netloc):
                        return jsonify({'success': True, 'auth_url': success})

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
    global ytcm_youtube_chat_reader
    
    try:
        received_state = request.args.get('state')
        code = request.args.get('code')
        error = request.args.get('error') # Handle potential errors from Google

        if error:
            if YTCM_DEBUG_MODE:
                logger.error(f"OAuth error from Google: {error}")
            print(f"Error from Google: {error}", 400)

        if not received_state:
            if YTCM_DEBUG_MODE:
                logger.error("Invalid OAuth state parameter")
            print("Invalid state parameter", 400)

        if not code:
            if YTCM_DEBUG_MODE:
                logger.error("Authorization code not found")
            print("Authorization code not found", 400)

        try:
            if not ytcm_youtube_chat_reader:
                ytcm_youtube_chat_reader = YouTubeChatReader()
            flow = ytcm_youtube_chat_reader.get_flow()
            flow.fetch_token(code=code)
        except Exception as e:
            if YTCM_DEBUG_MODE:
                logger.error(f"Failed to fetch token: {e}")
            flow = None

        if flow:
            # Credentials are now available in flow.credentials
            credentials = flow.credentials
            with open(YTCM_YT_TOKEN_FILE, 'w') as token:
                token.write(credentials.to_json())

            ytcm_youtube_chat_reader.youtube = build('youtube', 'v3', credentials=credentials)
            ytcm_youtube_chat_reader.connected = True

        return redirect(url_for('ytcm_index'))    
        
    except Exception as e:
        if YTCM_DEBUG_MODE:
            logger.error(f"Error during login callback: {str(e)}")
        return jsonify({'success': False, 'error': f"Error during login callback: {e}"})

@app.route('/ytcm_disconnect', methods=['POST'])
def ytcm_disconnect():
    global ytcm_youtube_chat_reader, ytcm_openai_service, ytcm_polly_service, ytcm_chat_messages
    
    try:
        if ytcm_youtube_chat_reader:
            ytcm_youtube_chat_reader.disconnect()
            ytcm_youtube_chat_reader = None
        
        if ytcm_openai_service:
            ytcm_openai_service = not ytcm_ai_needed
        
        # Clear messages
        ytcm_chat_messages = []
        ytcm_clear_audio_files()
        
        if YTCM_TRACE_MODE:
            logger.info("YouTube disconnection successful")
        
        return jsonify({'success': True})
    
    except Exception as e:
        if YTCM_DEBUG_MODE:
            logger.error(f"Error during disconnection: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/ytcm_toggle_message_visibility', methods=['POST'])
def ytcm_toggle_message_visibility():
    global ytcm_chat_messages, ytcm_hidden_msg_ids
    
    try:
        # Get message ID and new show value from request
        data = request.get_json()
        message_id = data.get('id')
        show_value = data.get('show', True)
        
        if not message_id:
            return jsonify({'success': False, 'error': 'Message ID is required'})

        if not show_value:
            ytcm_hidden_msg_ids.add(message_id)
        
        # Find the message with the given ID
        message_found = False
        for msg in ytcm_chat_messages:
            if msg.id == message_id:
                msg.show = show_value
                message_found = True
                if YTCM_TRACE_MODE:
                    logger.info(f"Message visibility changed: {msg.id} - show: {show_value}")
                break
        
        ytcm_chat_messages = [p for p in ytcm_chat_messages if p.id not in ytcm_hidden_msg_ids and p.show]

        if not message_found:
            return jsonify({'success': False, 'error': 'Message not found'})
        
        return jsonify({'success': True})
    
    except Exception as e:
        if YTCM_DEBUG_MODE:
            logger.error(f"Error toggling message visibility: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/ytcm_get_messages')
def ytcm_get_messages():
    global ytcm_youtube_chat_reader, ytcm_openai_service, ytcm_chat_messages, ytcm_last_live_chat_id, logger
    
    try:
        if not ytcm_youtube_chat_reader or not ytcm_openai_service:
            return jsonify({'success': False, 'error': 'Not connected to YouTube'})
        
        # Reading new messages from YouTube chat
        new_messages = ytcm_youtube_chat_reader.get_new_messages()
        if new_messages == False:
            ytcm_chat_messages = []
            ytcm_clear_audio_files()
            return jsonify({'success': True, 'messages': [], 'error': 'No live stream found on the channel'})
            
        live_chat_id = ytcm_youtube_chat_reader.live_chat_id
        if live_chat_id != ytcm_last_live_chat_id:
            ytcm_last_live_chat_id = live_chat_id
            ytcm_chat_messages = []
            ytcm_clear_audio_files()
            if YTCM_TRACE_MODE:
                try:
                    logger.info(f"Live chat ID changed: {live_chat_id}")
                except (OSError, IOError) as e:
                    # Handle stale file handle errors during logging
                    print(f"Logging error (handled): {str(e)}")
                    # Attempt to reset logger handlers
                    logger = setup_logger()
                
        for msg in new_messages:
            # Verify that the message has at least minimum words
            words = msg['text'].split()
            if len(words) >= YTCM_MIN_MESSAGE_WORDS:
                if YTCM_TRACE_MODE:
                    try:
                        logger.info(f"New message received: {msg['author']} - {msg['text']}")
                    except (OSError, IOError) as e:
                        # Handle stale file handle errors during logging
                        print(f"Logging error (handled): {str(e)}")
                        # Attempt to reset logger handlers
                        logger = setup_logger()
                
                # Verify if the message is a question via OpenAI
                is_question = (not YTCM_QUESTIONS_ONLY) or ytcm_openai_service.is_question(msg['text'])
                
                if is_question and ((not YTCM_APPLY_MODERATION) or ytcm_openai_service.is_appropriate(msg['text'])):
                    msg_text = msg['text']
                    if YTCM_APPLY_SPELLING_CORRECTION:
                        # Correct spelling and improve text form while preserving special placeholders
                        msg_text = ytcm_openai_service.correct_text(msg_text)
                    # Create a new custom message
                    chat_msg = ytcm_ChatMessageCustom(msg['author'], msg_text, (not YTCM_RETRIEVE_MSG_AUTHOR_GENDER) or ytcm_openai_service.is_male_username(msg['author']), msg['text'])
                    if chat_msg.id in ytcm_hidden_msg_ids:
                        chat_msg.show = False
                    if not ytcm_find_message(chat_msg):
                        if chat_msg.show:
                            ytcm_chat_messages.append(chat_msg)
                        ytcm_chat_messages = [p for p in ytcm_chat_messages if p.id not in ytcm_hidden_msg_ids and p.show]
                        if YTCM_TRACE_MODE:
                            try:
                                logger.info(f"Message added to the list: {chat_msg}")
                            except (OSError, IOError) as e:
                                # Handle stale file handle errors during logging
                                print(f"Logging error (handled): {str(e)}")
                                # Attempt to reset logger handlers
                                logger = setup_logger()
        
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
        try:
            if YTCM_DEBUG_MODE:
                logger.error(f"Error reading messages: {str(e)}")
        except (OSError, IOError) as log_err:
            # Handle stale file handle errors during error logging
            print(f"Logging error (handled): {str(log_err)}")
            # Attempt to reset logger handlers
            logger = setup_logger()
            
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Create necessary directories
    if not os.path.exists('config'):
        os.makedirs('config')
    
    # Create the directory for audio files if it doesn't exist
    if not os.path.exists(audio_file_dir_full_path):
        os.makedirs(audio_file_dir_full_path)
    
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
    
    # Create the example file for AWS Polly credentials if it doesn't exist
    if not os.path.exists(YTCM_POLLY_CONFIG_FILE):
        with open(YTCM_POLLY_CONFIG_FILE, 'w') as f:
            json.dump({
                "aws_access_key_id": "YOUR_AWS_ACCESS_KEY_ID",
                "aws_secret_access_key": "YOUR_AWS_SECRET_ACCESS_KEY",
                "region_name": "eu-west-1"
            }, f, indent=4)

    # Start the application
    app.run(debug=YTCM_DEBUG_MODE)