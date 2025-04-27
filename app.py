from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import datetime
from ytcm_youtube_chat_reader import YouTubeChatReader
from ytcm_openai_service import OpenAIService
from ytcm_polly_service import PollyService
from ytcm_consts import *
from googleapiclient.discovery import build
from urllib.parse import urlparse
import hashlib
from ytcm_messages_manager import ytcm_ChatMessagesManager, ytcm_HiddenMessagesManager
from ytcm_utils import *

app = Flask(__name__)

ytcm_ai_needed = YTCM_APPLY_MODERATION or YTCM_QUESTIONS_ONLY or YTCM_RETRIEVE_MSG_AUTHOR_GENDER or YTCM_APPLY_SPELLING_CORRECTION

# Check if TTS service is enabled
ytcm_tts_enabled = bool(YTCM_MALE_TTS_VOICE or YTCM_FEMALE_TTS_VOICE)

def get_audio_file_dir_full_path(): 
    return os.path.abspath(os.path.join(os.path.dirname(__file__), YTCM_TTS_AUDIO_FILES_DIR))

audio_file_dir_full_path = get_audio_file_dir_full_path()

channel_name = '...'

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

    def __repr__(self):
        return f"ytcm_ChatMessageCustom(id='{self.id}', author='{self.author}', raw_text={self.raw_text})"

ytcm_last_live_chat_id = None
ytcm_live_chat_first_change = True

# Inizializzazione dei gestori dei messaggi
ytcm_chat_messages_manager = ytcm_ChatMessagesManager()
ytcm_hidden_messages_manager = ytcm_HiddenMessagesManager()

# Service instances
ytcm_youtube_chat_reader = None
ytcm_openai_service = not ytcm_ai_needed
ytcm_polly_service = None

def ytcm_find_message(message: ytcm_ChatMessageCustom) -> bool:
    global ytcm_chat_messages_manager
    found = ytcm_chat_messages_manager.find_message(message)
    if found and YTCM_TRACE_MODE:
        info_log(f"Message found in the list: {message}")
    return found

# Loading configurations
def ytcm_load_config(config_file):
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        err_log(f"Error loading configuration file {config_file}: {str(e)}")
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
                info_log(f"Deleted audio file: {filename}")
        
        info_log(f"Cleared {deleted_count} audio files from {audio_file_dir_full_path}")
        
        return jsonify({'success': True, 'message': f'Deleted {deleted_count} audio files'})
    
    except Exception as e:
        err_log(f"Error clearing audio files: {str(e)}")
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
        err_log(f"Error generating audio: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/')
def ytcm_index():
    global channel_name
    ytcm_connect(True)
    live_title = ytcm_youtube_chat_reader.get_live_title() if ytcm_youtube_chat_reader else '[NO LIVE STREAM IN PROGRESS]'
    channel_name = ytcm_youtube_chat_reader.get_channel_name() if ytcm_youtube_chat_reader else '...'
    return render_template('ytcm_index.html', connected=ytcm_youtube_chat_reader is not None, polling_interval=YTCM_POLLING_INTERVAL_MS, live_title=live_title, channel_name=channel_name, tts_enabled=ytcm_tts_enabled, tts_audio_files_dir=YTCM_TTS_AUDIO_FILES_DIR, layout_style=YTCM_LAYOUT_STYLE, force_msg_uppercase=YTCM_FORCE_MSG_UPPERCASE)

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
                info_log("YouTube connection resumed")
            else:
                info_log("YouTube connection in progress...")
                # Clear messages
                ytcm_chat_messages = []
                ytcm_clear_audio_files()
                if isinstance(success, str):
                    res = urlparse(success)
                    if all([res.scheme, res.netloc]) and (res.scheme == 'https') and ('.' in res.netloc):
                        return jsonify({'success': True, 'auth_url': success})

            return jsonify({'success': True})
        else:
            err_log("Error connecting to YouTube")
            ytcm_disconnect()
            return jsonify({'success': False, 'error': 'Error connecting to YouTube'})
    
    except Exception as e:
        err_log(f"Error during connection: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/ytcm_oauth2callback')
def ytcm_oauth2callback():
    global ytcm_youtube_chat_reader
    
    try:
        received_state = request.args.get('state')
        code = request.args.get('code')
        error = request.args.get('error') # Handle potential errors from Google

        if error:
            err_log(f"OAuth error from Google: {error}")
            print(f"Error from Google: {error}", 400)

        if not received_state:
            err_log("Invalid OAuth state parameter")
            print("Invalid state parameter", 400)

        if not code:
            err_log("Authorization code not found")
            print("Authorization code not found", 400)

        try:
            if not ytcm_youtube_chat_reader:
                ytcm_youtube_chat_reader = YouTubeChatReader()
            flow = ytcm_youtube_chat_reader.get_flow()
            flow.fetch_token(code=code)
        except Exception as e:
            err_log(f"Failed to fetch token: {e}")
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
        err_log(f"Error during login callback: {str(e)}")
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
        
        info_log("YouTube disconnection successful")
        
        return jsonify({'success': True})
    
    except Exception as e:
        err_log(f"Error during disconnection: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/ytcm_toggle_message_visibility', methods=['POST'])
def ytcm_toggle_message_visibility():
    global ytcm_chat_messages_manager, ytcm_hidden_messages_manager
    
    try:
        # Get message ID and new show value from request
        data = request.get_json()
        message_id = data.get('id')
        show_value = data.get('show', False)
        
        if not message_id:
            return jsonify({'success': False, 'error': 'Message ID is required'})

        # Aggiorna la visibilità nel gestore degli ID nascosti
        if not show_value:
            ytcm_hidden_messages_manager.add_hidden_id(message_id)
#        else:
#            ytcm_hidden_messages_manager.remove_hidden_id(message_id)
        
            # Aggiorna la visibilità nel gestore dei messaggi
            message_found = ytcm_chat_messages_manager.update_message_visibility(message_id, show_value)
            
            if message_found:
                info_log(f"Message visibility changed: {message_id} - show: {show_value}")

            if not message_found:
                return jsonify({'success': False, 'error': 'Message not found'})
        
        return jsonify({'success': True})
    
    except Exception as e:
        err_log(f"Error toggling message visibility: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/ytcm_get_messages')
def ytcm_get_messages():
    global ytcm_youtube_chat_reader, ytcm_openai_service, ytcm_chat_messages_manager, ytcm_hidden_messages_manager, ytcm_last_live_chat_id, ytcm_live_chat_first_change
    
    try:
        clean_msg_list = False
        current_live_title = ''
        if not ytcm_youtube_chat_reader or not ytcm_openai_service:
            return jsonify({'success': False, 'error': 'Not connected to YouTube'})
            
        live_chat_id = ytcm_youtube_chat_reader.get_live_chat_id()
        if live_chat_id != ytcm_last_live_chat_id:            
            ytcm_last_live_chat_id = live_chat_id
            
            if ytcm_live_chat_first_change:
                info_log(f"First change of live chat ID: {live_chat_id}")
            else:
                info_log(f"Live ID changed: {live_chat_id}")
            
#            current_live_title = ytcm_youtube_chat_reader.get_live_title()
            
            if live_chat_id != False:
                ytcm_chat_messages_manager.clear_messages()            
                ytcm_hidden_messages_manager.clear_hidden_ids(not ytcm_live_chat_first_change)
                ytcm_clear_audio_files()
                ytcm_live_chat_first_change = None
                clean_msg_list = True
        elif not ytcm_live_chat_first_change:
            ytcm_live_chat_first_change = False
        
#        if current_live_title:
        current_live_title = {'live_title': ytcm_youtube_chat_reader.get_live_title()}
        if clean_msg_list:
            current_live_title['clean_msg_list'] = True
        info_log(f"Live title: {current_live_title}")

        # Reading new messages from YouTube chat
        new_messages = ytcm_youtube_chat_reader.get_new_messages()
        
        info_log(f"New messages from Google server: {new_messages}")

        if new_messages == False:
        
            err_log("Reading messages a communication error occurred with the Google server", None)

            return jsonify({'success': False, 'error': 'Oops! We couldn’t reach the Google server. \nIt looks like your query limit might be used up. \nThe query quota may have been exceeded. Please check your account limits.'})

        if (new_messages == None) or ((len(new_messages) == 0) and (current_live_title == None)):
            ytcm_chat_messages_manager.clear_messages()
            ytcm_clear_audio_files()

        if not new_messages:
            if current_live_title:
                message_ls = [current_live_title]
                return jsonify({'success': True, 'messages': message_ls, 'error': 'No live stream found on the channel'})
                            
        for msg in new_messages:
            # Verify that the message has at least minimum words
            words = msg['text'].split()
            if ((not YTCM_IGNORE_CHANNEL_OWNER_MESSAGES) or (msg['author'] != channel_name)) and (len(words) >= YTCM_MIN_MESSAGE_WORDS):
                
                info_log(f"New message received: {msg['author']} - {msg['text']}")
                
                # Verify if the message is a question via OpenAI
                is_question = (not YTCM_QUESTIONS_ONLY) or ytcm_openai_service.is_question(msg['text'])
                
                if is_question and ((not YTCM_APPLY_MODERATION) or ytcm_openai_service.is_appropriate(msg['text'])):
                    msg_text = msg['text']
                    if YTCM_APPLY_SPELLING_CORRECTION:
                        # Correct spelling and improve text form while preserving special placeholders
                        msg_text = ytcm_openai_service.correct_text(msg_text)
                    # Create a new custom message
                    chat_msg = ytcm_ChatMessageCustom(msg['author'], msg_text, (not YTCM_RETRIEVE_MSG_AUTHOR_GENDER) or ytcm_openai_service.is_male_username(msg['author']), msg['text'])
                    
                    # Verifica se il messaggio è nascosto
                    if ytcm_hidden_messages_manager.is_hidden(chat_msg.id):
                        chat_msg.show = False
                    
                    # Aggiungi il messaggio se non è già presente
                    if ytcm_chat_messages_manager.find_message(chat_msg):
                        if not chat_msg.show:
                            ytcm_chat_messages_manager.update_message_visibility(chat_msg.id, False)
                    else:
                        if chat_msg.show:
                            ytcm_chat_messages_manager.add_message(chat_msg)
                                                    
                            info_log(f"Message added to the list: {chat_msg}")
        
        # Format messages for the response
        formatted_messages = [{
            'id': msg.id,
            'author': msg.author,
            'text': msg.text,
            'datetime': msg.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'is_male': msg.is_male,
            'show': msg.show,
            'live_title': None
        } for msg in ytcm_chat_messages_manager.get_messages() if msg.show]

        if current_live_title:
            formatted_messages.insert(0, current_live_title)
                                    
            info_log(f"Sending messages with live title: {formatted_messages}")

        return jsonify({'success': True, 'messages': formatted_messages})
    
    except Exception as e:
        err_log(f"Error reading messages: {str(e)}")
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