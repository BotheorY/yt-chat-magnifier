import os
import json
import datetime
from ytcm_utils import *

class ytcm_ChatMessagesManager:
    """Class for managing chat messages, saving them in a JSON file."""
    
    def __init__(self, file_path=os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data')), 'ycm-chat_messages.json')):
        """Initialize the chat messages manager.
        
        Args:
            file_path (str): Path of the JSON file to save messages.
        """
        
        info_log(f"Initializing ytcm_ChatMessagesManager with file: {file_path}")

        self.messages = []
        self.file_path = file_path
        self._ensure_directory_exists()
        self._load_messages()
    
    def _ensure_directory_exists(self):
        """Ensure that the directory for the JSON file exists."""
        directory = os.path.dirname(os.path.abspath(self.file_path))
        if not os.path.exists(directory):            
            info_log(f"Creating directory: {directory}")
            os.makedirs(directory)
        else:
            info_log(f"Directory already exists: {directory}")
    
    def _load_messages(self):
        """Load messages from the JSON file if it exists."""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert dictionaries to objects compatible with ytcm_ChatMessageCustom
                    self.messages = []
                    for msg_dict in data:
                        # Recreate the object with the same attributes
                        msg = type('ytcm_ChatMessageCustom', (), {})()
                        for key, value in msg_dict.items():
                            if key == 'datetime':
                                # Convert the datetime string to a datetime object
                                value = datetime.datetime.fromisoformat(value)
                            setattr(msg, key, value)
                        self.messages.append(msg)            
            info_log(f"Loaded {len(self.messages)} messages from file {self.file_path}")
        except Exception as e:
            err_log(f"Error loading messages: {str(e)}")
            self.messages = []
    
    def _save_messages(self):
        """Save messages to the JSON file."""
        try:
            # Convert objects to serializable dictionaries
            serializable_messages = []
            for msg in self.messages:
                msg_dict = {}
                for key, value in msg.__dict__.items():
                    if key == 'datetime':
                        # Convert the datetime object to a string
                        value = value.isoformat()
                    msg_dict[key] = value
                serializable_messages.append(msg_dict)
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_messages, f, ensure_ascii=False, indent=2)
            info_log(f"Saved {len(serializable_messages)} messages to file {self.file_path}")
        except Exception as e:
            err_log(f"Error saving messages: {str(e)}")
    
    def add_message(self, message):
        """Add a message to the list and save.
        
        Args:
            message: Message object to add.
        """
        self._load_messages()
        eq_ids = [m for m in self.messages if m.id == message.id]
        if (not eq_ids) or (len(eq_ids) == 0):
            self.messages.append(message)
            self._save_messages()
            info_log(f"Message added with ID: {message.id}")
        else:
            info_log(f"Message already exists, not added: {message.id}")
    
    def remove_message(self, message_id):
        """Remove a message from the list and save.
        
        Args:
            message_id (str): ID of the message to remove.
        
        Returns:
            bool: True if the message was removed, False otherwise.
        """
        self._load_messages()
        for i, msg in enumerate(self.messages):
            if msg.id == message_id:
                del self.messages[i]
                self._save_messages()
                info_log(f"Message removed with ID: {message_id}")
                return True
        err_log(f"Attempt to remove message not found with ID: {message_id}")
        return False
    
    def get_messages(self):
        """Return all messages.
        
        Returns:
            list: List of all messages.
        """
        self._load_messages()
        return self.messages
    
    def clear_messages(self):
        """Delete all messages and save."""
        count = len(self.messages)
        self.messages = []
        self._save_messages()
        info_log(f"Deleted {count} messages from the list")
    
    def find_message(self, message):
        """Check if a message is already in the list.
        
        Args:
            message: Message object to search for.
        
        Returns:
            bool: True if the message was found, False otherwise.
        """
        self._load_messages()
        for msg in self.messages:
            if str(msg) == str(message):
                return True
        return False
    
    def update_message_visibility(self, message_id, show_value):
        """Update the visibility of a message.
        
        Args:
            message_id (str): ID of the message to update.
            show_value (bool): New visibility value.
        
        Returns:
            bool: True if the message was updated, False otherwise.
        """
        self._load_messages()
        for msg in self.messages:
            if msg.id == message_id:
                msg.show = show_value
                self._save_messages()
                info_log(f"Updated message visibility {message_id} to {show_value}")
                return True
        info_log(f"Attempt to update visibility for message not found: {message_id}")
        return False


class ytcm_HiddenMessagesManager:
    """Class for managing hidden message IDs, saving them in a JSON file."""
    
    def __init__(self, file_path=os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data')), 'ycm-hidden_messages.json')):
        """Initialize the hidden message IDs manager.
        
        Args:
            file_path (str): Path of the JSON file to save the IDs.
        """
        self.hidden_msg_ids = set()
        self.file_path = file_path
        info_log(f"Initializing ytcm_HiddenMessagesManager with file: {file_path}")
        self._ensure_directory_exists()
        self._load_hidden_ids()
    
    def _ensure_directory_exists(self):
        """Ensure that the directory for the JSON file exists."""
        directory = os.path.dirname(os.path.abspath(self.file_path))
        if not os.path.exists(directory):
            info_log(f"Creating directory: {directory}")
            os.makedirs(directory)
        else:
            info_log(f"Directory already exists: {directory}")
    
    def _load_hidden_ids(self):
        """Load hidden message IDs from the JSON file if it exists."""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.hidden_msg_ids = set(json.load(f))
                info_log(f"Loaded {len(self.hidden_msg_ids)} hidden IDs from file {self.file_path}")
        except Exception as e:
            err_log(f"Error loading hidden IDs: {str(e)}")
            self.hidden_msg_ids = set()
    
    def _save_hidden_ids(self):
        """Save hidden message IDs to the JSON file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(list(self.hidden_msg_ids), f, ensure_ascii=False, indent=2)
            info_log(f"Saved {len(self.hidden_msg_ids)} hidden IDs to file {self.file_path}")
        except Exception as e:
            err_log(f"Error saving hidden IDs: {str(e)}")
    
    def add_hidden_id(self, message_id):
        """Add an ID to the list of hidden IDs and save.
        
        Args:
            message_id (str): ID of the message to hide.
        """
        self._load_hidden_ids()
        self.hidden_msg_ids.add(message_id)
        self._save_hidden_ids()
        info_log(f"Added ID {message_id} to the hidden IDs list")
    
    def remove_hidden_id(self, message_id):
        """Remove an ID from the list of hidden IDs and save.
        
        Args:
            message_id (str): ID of the message to show.
        
        Returns:
            bool: True if the ID was removed, False otherwise.
        """
        self._load_hidden_ids()
        if message_id in self.hidden_msg_ids:
            self.hidden_msg_ids.remove(message_id)
            self._save_hidden_ids()
            info_log(f"Removed ID {message_id} from the hidden IDs list")
            return True
        info_log(f"Attempt to remove ID not found: {message_id}")
        return False
    
    def is_hidden(self, message_id):
        """Check if an ID is in the list of hidden IDs.
        
        Args:
            message_id (str): ID of the message to check.
        
        Returns:
            bool: True if the ID is hidden, False otherwise.
        """
        self._load_hidden_ids()
        return message_id in self.hidden_msg_ids
    
    def get_hidden_ids(self):
        """Return all hidden IDs.
        
        Returns:
            set: Set of all hidden IDs.
        """
        self._load_hidden_ids()
        return self.hidden_msg_ids
    
    def clear_hidden_ids(self, force=False):
        """Delete all hidden IDs and save."""
        self._load_hidden_ids()
        count = len(self.hidden_msg_ids)
        if force or (count > 1000):
            self.hidden_msg_ids = set()
            self._save_hidden_ids()
            info_log(f"Deleted {count} hidden IDs")
        else:
            info_log(f"No deletion of hidden IDs (count={count}, force={force})")
            self._load_hidden_ids()
