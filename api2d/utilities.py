import requests
import json
from dataclasses import dataclass
from datetime import datetime
import logging

class Api2dClient:
    """Client for interacting with the API2D API"""
    
    def __init__(self, api_key, base_url):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def call_custom_key_save(self, type_id, n):
        try:
            response = requests.post(f"{self.base_url}/custom_key/save", 
                        headers=self.headers, 
                        data=json.dumps({"type_id": type_id, "n": n}))
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()["data"]["custom_key_array"]
        except requests.exceptions.RequestException as e:
            # Log the error or handle it as needed
            logging.error(f"Error Creating API key info: {e}")
            return None

    def call_custom_key_search_key(self, key):
        try:
            # need to be replace with search key when external bug is fixed
            response = requests.post(f"{self.base_url}/custom_key/search_key", 
                        headers=self.headers, 
                        data=json.dumps({"query": key}))
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()["data"]["custom_key_array"]
        except requests.exceptions.RequestException as e:
            # Log the error or handle it as needed
            logging.error(f"Error fetching API key info: {e}")
            return None

    def get_key(self, key):
        key_array = self.call_custom_key_search_key(key)
        if len(key_array) > 1:
            raise ValueError("Multiple keys are found. Please enter the complete key.")
        elif len(key_array) == 0:
            raise ValueError("Key not found. Please enter a valid key.")

        key_json = key_array[0]
        if not key_json["enabled"]:
            raise ValueError("Key is disabled. Please use a new key.")
        elif key_json["key"] != key:
            raise ValueError("Key is mismatched. Pleae contact support.")
        
        return Api2dCustomKey(
            id=key_json["id"],
            uid=key_json["uid"],
            key=key_json["key"],
            type_id=key_json["type_id"],
            created_at=key_json["created_at"],
            enabled=key_json["enabled"]
        )
    
@dataclass
class Api2dCustomKey():
    id: int
    uid: int
    key: str
    type_id: str
    created_at: datetime
    enabled: bool

