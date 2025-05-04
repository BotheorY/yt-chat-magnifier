import boto3
import os
import json
from ytcm_consts import *
from ytcm_utils import *

class PollyService:
    def __init__(self, credentials_file):
        self.polly_client = None
        self.initialized = False
        
        try:
            # Load AWS credentials
            if os.path.exists(credentials_file):
                with open(credentials_file, 'r') as f:
                    credentials = json.load(f)
                
                # Initialize Polly client
                self.polly_client = boto3.client(
                    'polly',
                    aws_access_key_id=credentials['aws_access_key_id'],
                    aws_secret_access_key=credentials['aws_secret_access_key'],
                    region_name=credentials['region_name']
                )
                self.initialized = True
                info_log("AWS Polly service initialized successfully")
            else:
                err_log(f"AWS Polly credentials file not found: {credentials_file}")
        except Exception as e:
            err_log(f"Error initializing AWS Polly service: {str(e)}")
    
    def is_available(self):
        """Checks if the Polly service is available"""
        return self.initialized and self.polly_client is not None
    
    def _clean_emoji_codes(self, text):
        """Removes YouTube emoji codes from the text"""
        import re
        # Removes all codes in the format :emoji-name: or :name:
        cleaned_text = re.sub(r':[a-zA-Z0-9-]+:', '', text)
        return cleaned_text
    
    def generate_audio(self, text, message_id, is_male=True):
        """Generates an MP3 audio file using AWS Polly"""
        if not self.is_available():
            err_log("AWS Polly service not available")
            return False
        try:
            # Cleans the text by removing emoji codes
            cleaned_text = self._clean_emoji_codes(text)
            info_log(f"Generating audio for message ID: {message_id}, text length: {len(cleaned_text)}")
            
            # Determines the voice to use based on gender
            voice_id = self._get_voice_id(is_male)
            if not voice_id:
                err_log("No voice configured for TTS")
                return False
                
            # Check that the text is not empty
            if not cleaned_text.strip():
                err_log(f"Empty text for message ID: {message_id}")
                return False
                
            # Limit the text length if necessary (Polly has a 3000 character limit)
            if len(cleaned_text) > 3000:
                cleaned_text = cleaned_text[:3000]
                info_log(f"Text truncated to 3000 characters for message ID: {message_id}")
                
            # Generates audio with Polly
            info_log(f"Calling Polly API with voice: {voice_id}")
            response = self.polly_client.synthesize_speech(
                Text=cleaned_text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                SampleRate='24000'
            )
            
            # Check that the response contains the AudioStream
            if 'AudioStream' not in response:
                err_log(f"No AudioStream in Polly response for message ID: {message_id}")
                return False
                
            # Creates the directory if it does not exist
            audio_file_dir_full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), YTCM_TTS_AUDIO_FILES_DIR))
            os.makedirs(audio_file_dir_full_path, exist_ok=True)
            
            # Saves the audio file
            file_path = os.path.join(audio_file_dir_full_path, f"{message_id}.mp3")
            with open(file_path, 'wb') as f:
                audio_data = response['AudioStream'].read()
                if not audio_data:
                    err_log(f"Empty audio data from Polly for message ID: {message_id}")
                    return False
                f.write(audio_data)
                
            info_log(f"Audio file generated successfully: {file_path}")
            return True
        except Exception as e:
            err_log(f"Error generating audio file for message ID: {message_id}, error: {str(e)}")
            # Log more detailed error information for debugging
            import traceback
            err_log(f"Detailed error: {traceback.format_exc()}")
            return False
    
    def _get_voice_id(self, is_male):
        """Determines the voice ID to use based on gender"""
        # If only one of the two voices is configured, use that one
        if YTCM_MALE_TTS_VOICE and not YTCM_FEMALE_TTS_VOICE:
            return YTCM_MALE_TTS_VOICE
        elif YTCM_FEMALE_TTS_VOICE and not YTCM_MALE_TTS_VOICE:
            return YTCM_FEMALE_TTS_VOICE
        # If both are configured, choose based on gender
        elif YTCM_MALE_TTS_VOICE and YTCM_FEMALE_TTS_VOICE:
            return YTCM_MALE_TTS_VOICE if is_male else YTCM_FEMALE_TTS_VOICE
        # If none is configured, return None
        return None