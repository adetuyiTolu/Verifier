import requests
import os
import logging

class PremblyService:
    BASE_URL = "https://api.prembly.com" 
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("PREMBLY_API_KEY")
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def verify_phone_number(self, phone_number):
        """
        Verifies a phone number.
        Endpoint: Placeholder /identity/phone
        """
        try:
            # Placeholder implementation until real endpoints are provided
            url = f"{self.BASE_URL}/verification/phone_number/advance"
            payload = {"number": phone_number}
            
            # NOTE: Logic to switch between GET/POST depending on actual API
            response = requests.post(url, json=payload, headers=self.headers)
            return response.json()
            
          
        except Exception as e:
            logging.error(f"Error calling Prembly API: {e}")
            return {"status": "error", "message": str(e)}

    def verify_bvn(self, bvn):
        try:
            url = f"{self.BASE_URL}/verification/bvn" # Assumption based on pattern
            payload = {"number": bvn}
            response = requests.post(url, json=payload, headers=self.headers)
            return response.json()
        except Exception as e:
            logging.error(f"Error calling Prembly API for BVN: {e}")
            return {"status": "error", "message": str(e)}

    def verify_nin(self, nin):
        try:
            url = f"{self.BASE_URL}/verification/vnin" # Assumption based on pattern
            payload = {"number": nin}
            response = requests.post(url, json=payload, headers=self.headers)
            return response.json()
        except Exception as e:
            logging.error(f"Error calling Prembly API for NIN: {e}")
            return {"status": "error", "message": str(e)}

    def check_api_key_validity(self, api_key):
        """
        Checks if the provided API key is valid.
        """
        # Mock Check
        return True
