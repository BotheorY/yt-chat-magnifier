import os
from flask import request
from ytcm_consts import *
import json
from ytcm_utils import *

# Logging functions imported from ytcm_utils
# info_log - For informational messages
# err_log - For error messages

"""
Data persistence system with deep change monitoring

This module implements a data persistence system that automatically monitors
changes to nested data structures (lists and dictionaries) and triggers saving
when they are modified. This allows automatic saving when an element
of a dictionary contained in a list is modified through the singleton instance.

Usage example:
    ytcm_data.my_list = [{"key": "value"}]  # Creates a list with a dictionary
    ytcm_data.my_list[0]["key"] = "new value"  # Modifies the dictionary -> automatic saving
"""


class ObservableDict(dict):
    """A dictionary that notifies a callback when modified."""
    def __init__(self, *args, callback=None, **kwargs):
        """Initializes the observable dictionary.
        
        Args:
            callback: Function to call when the dictionary is modified.
        """
        self._callback = callback
        super().__init__(*args, **kwargs)
        
        # Wraps existing elements
        for key, value in list(self.items()):
            super().__setitem__(key, self._wrap_value(value))
        
    def _wrap_value(self, value):
        """Wraps values in observable wrappers if necessary."""
        if isinstance(value, dict) and not isinstance(value, ObservableDict):
            return ObservableDict(value, callback=self._callback)
        elif isinstance(value, list) and not isinstance(value, ObservableList):
            return ObservableList(value, callback=self._callback)
        return value
        
    def set_callback(self, callback):
        """Sets the callback for this dictionary and all its observable elements.
        
        Args:
            callback: The function to call when the dictionary is modified.
        """
        self._callback = callback
        
        # Updates the callback for all observable elements
        for key, value in self.items():
            if isinstance(value, (ObservableDict, ObservableList)):
                value.set_callback(callback)
        
    def __setitem__(self, key, value):
        """Intercepts value assignment and notifies the callback."""
        wrapped_value = self._wrap_value(value)
        super().__setitem__(key, wrapped_value)
        if self._callback:
            self._callback()
            
    def update(self, *args, **kwargs):
        """Intercepts dictionary update and notifies the callback."""
        if args:
            other = args[0]
            if isinstance(other, dict):
                for key, value in other.items():
                    self[key] = value
            else:
                for key, value in other:
                    self[key] = value
        for key, value in kwargs.items():
            self[key] = value
        if self._callback:
            self._callback()

class ObservableList(list):
    """A list that notifies a callback when modified."""
    def __init__(self, *args, callback=None, **kwargs):
        """Initializes the observable list.
        
        Args:
            callback: Function to call when the list is modified.
        """
        self._callback = callback
        super().__init__(*args, **kwargs)
        # Wraps existing elements
        for i, item in enumerate(self):
            self[i] = self._wrap_value(item)
    
    def _wrap_value(self, value):
        """Wraps values in observable wrappers if necessary."""
        if isinstance(value, dict) and not isinstance(value, ObservableDict):
            return ObservableDict(value, callback=self._callback)
        elif isinstance(value, list) and not isinstance(value, ObservableList):
            return ObservableList(value, callback=self._callback)
        return value
        
    def set_callback(self, callback):
        """Sets the callback for this list and all its observable elements.
        
        Args:
            callback: The function to call when the list is modified.
        """
        self._callback = callback
        
        # Updates the callback for all observable elements
        for i, value in enumerate(self):
            if isinstance(value, (ObservableDict, ObservableList)):
                value.set_callback(callback)
    
    def __setitem__(self, index, value):
        """Intercepts value assignment and notifies the callback."""
        wrapped_value = self._wrap_value(value)
        super().__setitem__(index, wrapped_value)
        if self._callback:
            self._callback()
    
    def append(self, value):
        """Intercepts value addition and notifies the callback."""
        wrapped_value = self._wrap_value(value)
        super().append(wrapped_value)
        if self._callback:
            self._callback()
    
    def extend(self, iterable):
        """Intercepts list extension and notifies the callback."""
        for item in iterable:
            self.append(item)
        if self._callback:
            self._callback()
    
    def insert(self, index, value):
        """Intercepts value insertion and notifies the callback."""
        wrapped_value = self._wrap_value(value)
        super().insert(index, wrapped_value)
        if self._callback:
            self._callback()
    
    def pop(self, index=-1):
        """Intercepts value removal and notifies the callback."""
        result = super().pop(index)
        if self._callback:
            self._callback()
        return result
    
    def remove(self, value):
        """Intercepts value removal and notifies the callback."""
        super().remove(value)
        if self._callback:
            self._callback()

class DataBag:
    """Base class for storing application data in memory.
    
    This class holds various runtime states and configuration settings for the application.
    It is not persisted to disk directly but serves as the data model for StoredDataBag.
    """
    def __init__(self):
        """Initialize the DataBag with default values.
        
        Sets up runtime flags, configuration settings, and initializes message managers.
        """
        info_log("Initializing DataBag instance")
        # Operation flags
        self.ytcm_get_messages_in_progress = False
        self.last_formatted_messages = []
        
        # AI service configuration
        self.ytcm_ai_needed = YTCM_APPLY_MODERATION or YTCM_QUESTIONS_ONLY or YTCM_RETRIEVE_MSG_AUTHOR_GENDER or YTCM_APPLY_SPELLING_CORRECTION
        
        # Text-to-Speech configuration
        self.ytcm_tts_enabled = YTCM_MALE_TTS_VOICE or YTCM_FEMALE_TTS_VOICE
        self.audio_file_dir_full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), YTCM_TTS_AUDIO_FILES_DIR))
        
        # YouTube chat data
        self.channel_name = '...'
        self.ytcm_last_live_chat_id = None
        self.ytcm_live_chat_first_change = True

        info_log("DataBag initialization complete")
        
    def __setattr__(self, name, value):
        """Intercepts attribute assignment to wrap lists and dictionaries.
        
        This method ensures that all lists and dictionaries assigned as attributes
        are automatically wrapped in their respective observable wrappers.
        
        Args:
            name: The name of the attribute to set
            value: The value to assign to the attribute
        """
        # Wraps the value if it's a list or dictionary
        # Note: we cannot pass the callback here because we don't have access to StoredDataBag._save
        # The wrappers will be reconfigured with the appropriate callback when loaded by StoredDataBag
        if isinstance(value, list) and not isinstance(value, ObservableList):
            value = ObservableList(value)
        elif isinstance(value, dict) and not isinstance(value, ObservableDict):
            value = ObservableDict(value)
            
        # Assigns the (possibly wrapped) value to the attribute
        super().__setattr__(name, value)

class StoredDataBag:
    """Persistent data storage wrapper for DataBag.
    
    This class provides persistence for DataBag by saving and loading its state to/from a JSON file.
    It implements various Python special methods to make it behave like the underlying DataBag instance.
    """

    def __init__(self, file_path=os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data')), 'ycm-data.json')):
        """Initialize the StoredDataBag with a file path for persistence.
        
        Args:
            file_path: Path to the JSON file for data persistence. Defaults to 'data/ycm-data.json'
                       relative to the current script's directory.
        """
        info_log(f"Initializing StoredDataBag with file: {file_path}")
        self._data = DataBag()
        self._file_path = file_path
        self._save_enabled = True
        self._load_enabled = True
        info_log("StoredDataBag initialization complete")
        self._ensure_directory_exists()
        self._load()
    
    def _ensure_directory_exists(self):
        """Ensure that the directory for the JSON file exists."""
        directory = os.path.dirname(os.path.abspath(self._file_path))
        if not os.path.exists(directory):
            info_log(f"Creating directory: {directory}")
            os.makedirs(directory)
        else:
            info_log(f"Directory already exists: {directory}")
    
    def _save(self):
        """Save data to the JSON file.
        
        Serializes saveable attributes of the DataBag instance to JSON format.
        Only primitive types (int, float, str, list, dict, set, tuple, bool, None) are saved.
        Complex objects like lists and dictionaries are checked recursively for serializability.
        """
        if not self._save_enabled:
            return
        self._save_enabled = False
        self._load_enabled = False
        try:
            # Gets stack information to trace where the function was called from
            import traceback
            stack = traceback.extract_stack()
            # Ignore the last two frames (this method and the callback)
            caller_info = "unknown"
            if len(stack) > 2:
                frame = stack[-3]
                caller_info = f"{frame.filename}:{frame.lineno} in {frame.name}"
            
            info_log(f"Saving data to file: {self._file_path} (called from: {caller_info})")
            try:
                data_to_save = {}
                
                def is_json_serializable(obj):
                    """Check if an object is JSON serializable."""
                    if obj is None or isinstance(obj, (int, float, str, bool)):
                        return True
                    elif isinstance(obj, (list, tuple)):
                        return all(is_json_serializable(item) for item in obj)
                    elif isinstance(obj, dict):
                        return all(isinstance(k, str) and is_json_serializable(v) for k, v in obj.items())
                    elif isinstance(obj, set):
                        return all(is_json_serializable(item) for item in obj)
                    return False
                
                for attr_name in dir(self._data):
                    # Skip private/special attributes and methods
                    if attr_name.startswith('_') or callable(getattr(self._data, attr_name)):
                        continue
                        
                    value = getattr(self._data, attr_name)
                    
                    # Check if the value is JSON serializable
                    if is_json_serializable(value):
                        data_to_save[attr_name] = value
                    else:
                        info_log(f"Skipping non-serializable attribute: {attr_name}")
                
                info_log(f"Saving {len(data_to_save)} attributes to file")
                with open(self._file_path, 'w', encoding='utf-8') as f:
                    json.dump(data_to_save, f, ensure_ascii=False, indent=2)
                info_log("Data saved successfully")
            except Exception as e:
                err_log(f"Error saving data: {str(e)}")
        finally:
            self._save_enabled = True
            self._load_enabled = True

    def _load(self):
        """Load data from the JSON file if it exists.
        
        Deserializes the JSON data and updates the DataBag instance attributes.
        Only updates attributes that were previously saved and exist in the current DataBag instance.
        Ensures that lists and dictionaries are wrapped in their respective observable wrappers.
        """
        if not self._load_enabled:
            return
        self._load_enabled = False
        self._save_enabled = False
        try:
            info_log(f"Loading data from file: {self._file_path}")
            try:
                if os.path.exists(self._file_path):
                    with open(self._file_path, 'r', encoding='utf-8') as f:
                        saved_data = json.load(f)
                        # Update only the properties that were saved and exist in the current instance
                        loaded_count = 0
                        for attr_name, value in saved_data.items():
                            # Check if the attribute already exists in the DataBag instance
                            if hasattr(self._data, attr_name):
                                try:
                                    # Wraps lists and dictionaries in observable wrappers with the appropriate callback
                                    if isinstance(value, list):
                                        value = ObservableList(value, callback=self._save)
                                    elif isinstance(value, dict):
                                        value = ObservableDict(value, callback=self._save)
                                    
                                    setattr(self._data, attr_name, value)
                                    loaded_count += 1
                                except Exception as attr_err:
                                    err_log(f"Error setting attribute {attr_name}: {str(attr_err)}")
                            else:
                                info_log(f"Skipping unknown attribute: {attr_name}")
                        info_log(f"Loaded {loaded_count} of {len(saved_data)} attributes from file")
                        
                        # Configures callbacks for all existing attributes
                        self._configure_callbacks()
                else:
                    info_log("Data file does not exist, using default values")
            except Exception as e:
                err_log(f"Error loading data: {str(e)}")
        finally:
            self._load_enabled = True
            self._save_enabled = True
            
    def _configure_callbacks(self):
        """Configures callbacks for all existing observable attributes.
        
        This method ensures that all ObservableList and ObservableDict objects
        have the correct _save callback, even if they were created without a callback.
        """
        for attr_name in dir(self._data):
            if attr_name.startswith('_') or callable(getattr(self._data, attr_name)):
                continue
                
            value = getattr(self._data, attr_name)
            if isinstance(value, (ObservableList, ObservableDict)):
                value.set_callback(self._save)
            
    def get(self, var_name: str, default=None):
        """Get an attribute value from the DataBag instance.
        
        Args:
            var_name: The name of the attribute to retrieve
            default: The default value to return if the attribute doesn't exist
            
        Returns:
            The attribute value or the default value if not found
        """
#        info_log(f"Reading attribute: {var_name}")
        self._load()
        return getattr(self._data, var_name, default)

    def set(self, var_name: str, value):
        """Set an attribute value in the DataBag instance and save to disk.
        
        Args:
            var_name: The name of the attribute to set
            value: The value to assign to the attribute
        """
#        info_log(f"Setting attribute: {var_name}")
        self._load()
        
        # Avvolge liste e dizionari in wrapper osservabili
        if isinstance(value, list):
            value = ObservableList(value, callback=self._save)
        elif isinstance(value, dict):
            value = ObservableDict(value, callback=self._save)
            
        setattr(self._data, var_name, value)
        self._save()

    def __getattr__(self, var_name):
        return self.get(var_name)

    def __setattr__(self, var_name, value):
        if var_name.startswith('_'):
            super().__setattr__(var_name, value)
        else:
            self.set(var_name, value)

    def __getitem__(self, var_name):
        return self.get(var_name)

    def __setitem__(self, var_name, value):
        self.set(var_name, value)

    def __contains__(self, var_name):
        return hasattr(self._data, var_name)

    def __len__(self):
        self._load()
        return len(self._data)

    def __repr__(self):
        self._load()
        return repr(self._data)

    def __str__(self):
        self._load()
        return str(self._data)

    def __del__(self):
        self._save()

# Singleton pattern implementation
class StoredDataBagSingleton:
    """Singleton implementation for StoredDataBag.
    
    Ensures that only one instance of StoredDataBag exists throughout the application.
    Provides attribute access that delegates to the underlying StoredDataBag instance.
    """
    _instance = None

    def __new__(cls):
        """Create a new instance only if one doesn't already exist.
        
        Returns:
            The singleton instance of StoredDataBagSingleton
        """
        if cls._instance is None:
            info_log("Creating StoredDataBagSingleton instance")
            cls._instance = super(StoredDataBagSingleton, cls).__new__(cls)
            cls._instance._data_bag = StoredDataBag()
            info_log("StoredDataBagSingleton instance created")
        return cls._instance

    def __getattr__(self, attr):
        return getattr(self._data_bag, attr)

    def __setattr__(self, attr, value):
        if attr.startswith('_'):
            super().__setattr__(attr, value)
        else:
            setattr(self._data_bag, attr, value)

# Create an instance of the singleton for global use
info_log("Initializing global ytcm_data singleton")
ytcm_data = StoredDataBagSingleton()
info_log("Global ytcm_data singleton initialized")

# Example of using the observation system for lists and dictionaries
def test_observable_collections():
    """Test to demonstrate the functioning of the observation system for lists and dictionaries.
    
    This test shows how modifying a dictionary within a list
    automatically triggers data saving.
    """
    try:
        # Create a list of dictionaries
        ytcm_data.test_list = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ]
        
        # Modify an element of the dictionary in the list
        # This should trigger automatic saving
        ytcm_data.test_list[0]["name"] = "Item 1 Modified"
        
        info_log("Test completed successfully: modification of a dictionary in a list")
        return True
    except Exception as e:
        err_log(f"Error during test: {str(e)}")
        return False

# Run the test only if this file is executed directly
if __name__ == "__main__":
    test_observable_collections()
