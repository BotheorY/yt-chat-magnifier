import os
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from ytcm_consts import *
import json
from flask import request

logger = logging.getLogger('chat_magnifier')

class YouTubeChatReader:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/youtube.readonly']
        self.youtube = None
        self.live_chat_id = None
        self.next_page_token = None
        self.connected = False
        self.token_file = YTCM_YT_TOKEN_FILE
        self.redirect_uri = request.url_root + 'ytcm_oauth2callback'
    
    def connect(self, resume_only=False):
        """Connects to YouTube APIs and gets the live chat ID"""

        try:
            # Authentication with OAuth 2.0
            credentials, resumed = self._get_credentials(resume_only)

            if not credentials:
                if YTCM_DEBUG_MODE:
                    if resume_only:
                        logger.error("Failed to authenticate cause no credentials from file")
                    else:
                        logger.error("Failed to authenticate with OAuth 2.0")
                return False
            
            if isinstance(credentials, str):
                if YTCM_TRACE_MODE:
                    logger.info("Redirected to YouTube login page.")
                return credentials

            # Create YouTube service
            self.youtube = build('youtube', 'v3', credentials=credentials)
            
            self.connected = True
            return 'resumed' if resumed else True
        
        except HttpError as e:
            if YTCM_DEBUG_MODE:
                logger.error(f"HTTP error during YouTube connection: {str(e)}")
            return False
        except Exception as e:
            if YTCM_DEBUG_MODE:
                logger.error(f"Error during YouTube connection: {str(e)}")
            return False
    
    def _get_credentials(self, resume_only=False):
        """Gets OAuth 2.0 credentials"""
        credentials = None
        resumed = True
        
        # Load credentials from file if they exist
        if os.path.exists(self.token_file):
            try:
                credentials = Credentials.from_authorized_user_info(
                    json.loads(open(self.token_file).read()), self.scopes)
            except Exception as e:
                if YTCM_DEBUG_MODE:
                    logger.error(f"Error loading token: {str(e)}")
        
        # If there are no valid credentials, run the authentication flow
        if (not credentials) or (not credentials.valid):
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                except RefreshError as e:
                    if YTCM_DEBUG_MODE:
                        logger.error(f"Error refreshing token: {str(e)}")
                    credentials = None
            
            if (not resume_only) and (not credentials):
                resumed = False
                flow = self.get_flow()

                try:
                    auth_url, state = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
                    return auth_url, resumed
                except Exception as e:
                    logger.error(f"Errore durante il flusso OAuth Authorization Code Grant: {e}", exc_info=True)
                    credentials = None
            
            if credentials:
                # Save credentials for the next startup
                with open(self.token_file, 'w') as token:
                    token.write(credentials.to_json())
        
        return credentials, resumed
    
    def get_flow(self):
        flow = Flow.from_client_secrets_file(YTCM_GOOGLE_CONFIG_FILE, scopes=self.scopes, redirect_uri=self.redirect_uri)
        return flow

    def _get_live_chat_id(self):
        """Gets the live chat ID from the authenticated channel"""
        try:
            # Get the list of active live broadcasts
            request = self.youtube.liveBroadcasts().list(
                part="snippet,contentDetails",
                broadcastStatus="active",
                maxResults=5
            )
            response = request.execute()
            
            # Search for the live chat ID
            for item in response.get('items', []):
                if 'liveChatId' in item['snippet']:
                    return item['snippet']['liveChatId']
            
            # If not found, try to search in livestreams
            request = self.youtube.liveStreams().list(
                part="snippet,cdn",
                mine=True,
                maxResults=5
            )
            response = request.execute()
            
            for item in response.get('items', []):
                if 'activeLiveChatId' in item['snippet']:
                    return item['snippet']['activeLiveChatId']
            
            return None
        
        except HttpError as e:
            if YTCM_DEBUG_MODE:
                logger.error(f"HTTP error while retrieving live chat ID: {str(e)}")
            return None
        except Exception as e:
            if YTCM_DEBUG_MODE:
                logger.error(f"Error while retrieving live chat ID: {str(e)}")
            return None
    
    def get_new_messages(self):
        """Gets new messages from the live chat"""

        if not self.connected:
            if YTCM_DEBUG_MODE:
                logger.error("Not connected to YouTube")
            return []

        # Get the live chat ID
        self.live_chat_id = self._get_live_chat_id()            
        if not self.live_chat_id:
            if YTCM_DEBUG_MODE:
                logger.error("No live stream found on the channel")
            return False
        
        try:
            # Request chat messages
            request = self.youtube.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part="snippet,authorDetails",
                pageToken=self.next_page_token
            )
            response = request.execute()
            
            # Update token for the next request
            self.next_page_token = response.get('nextPageToken')
            
            # Extract messages
            messages = []
            for item in response.get('items', []):
                if item['snippet']['type'] == 'textMessageEvent':
                    messages.append({
                        'author': item['authorDetails']['displayName'],
                        'text': item['snippet']['displayMessage'],
                        'published_at': item['snippet']['publishedAt']
                    })
            
            return messages
        
        except HttpError as e:
            if YTCM_DEBUG_MODE:
                logger.error(f"HTTP error during message retrieval: {str(e)}")
            return []
        except Exception as e:
            if YTCM_DEBUG_MODE:
                logger.error(f"Error during message retrieval: {str(e)}")
            return []
    
    def disconnect(self):
        """Disconnects from YouTube APIs"""
        self.youtube = None
        self.live_chat_id = None
        self.next_page_token = None
        self.connected = False
        # Delete the token file if it exists
        if os.path.exists(self.token_file):
            try:
                os.remove(self.token_file)
                if YTCM_TRACE_MODE:
                    logger.info(f"Removed token file: {self.token_file}")
            except Exception as e:
                if YTCM_DEBUG_MODE:
                    logger.error(f"Error removing token file: {str(e)}")

        if YTCM_TRACE_MODE:
            logger.info("Disconnected from YouTube")
        return True

    def get_live_title(self):
        """Gets the title of the current live stream"""

        if not self.connected:
            if YTCM_DEBUG_MODE:
                logger.error("Not connected to YouTube")
            return '...'

        try:
            # Get the list of active live broadcasts
            request = self.youtube.liveBroadcasts().list(
                part="snippet",
                broadcastStatus="active",
                maxResults=1
            )
            response = request.execute()

            # Get the title from the first active broadcast
            items = response.get('items', [])
            if items:
                return items[0]['snippet']['title']

            # If not found in broadcasts, try livestreams
            request = self.youtube.liveStreams().list(
                part="snippet",
                mine=True,
                maxResults=1
            )
            response = request.execute()

            items = response.get('items', [])
            if items:
                if items[0]['snippet']['isDefaultStream']:
                    return items[0]['snippet']['title']

            return '...'

        except HttpError as e:
            if YTCM_DEBUG_MODE:
                logger.error(f"HTTP error while retrieving live title: {str(e)}")
            return '...'
        except Exception as e:
            if YTCM_DEBUG_MODE:
                logger.error(f"Error while retrieving live title: {str(e)}")
            return '...'

    def get_channel_name(self):
        """Gets the name of the authenticated channel"""
        
        if not self.connected:
            if YTCM_DEBUG_MODE:
                logger.error("Not connected to YouTube")
            return '...'

        try:
            # Get the authenticated channel's information
            request = self.youtube.channels().list(
                part="snippet",
                mine=True
            )
            response = request.execute()

            # Get the channel name
            items = response.get('items', [])
            if items:
                return items[0]['snippet']['title']

            return '...'

        except HttpError as e:
            if YTCM_DEBUG_MODE:
                logger.error(f"HTTP error while retrieving channel name: {str(e)}")
            return '...'
        except Exception as e:
            if YTCM_DEBUG_MODE:
                logger.error(f"Error while retrieving channel name: {str(e)}")
            return '...'
