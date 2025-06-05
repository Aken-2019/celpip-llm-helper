import requests
import json
from dataclasses import dataclass
from datetime import datetime



class Api2dClient:
    def __init__(self, api_key, base_url):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
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
            print(f"Error fetching API key info: {e}")
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

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    API2D_API_ENDPOINT = os.getenv("DYNACONF_API2D_API_ENDPOINT")
    API2D_ADMIN_KEY = os.getenv("DYNACONF_API2D_ADMIN_KEY")
    client = Api2dClient(API2D_ADMIN_KEY, API2D_API_ENDPOINT)

    key = client.call_custom_key_search_key(os.getenv("DYNACONF_API2D_TEST_FORWARD_KEY"))
    print(key)

    class_key = client.get_key(os.getenv("DYNACONF_API2D_TEST_FORWARD_KEY"))
    print(class_key)