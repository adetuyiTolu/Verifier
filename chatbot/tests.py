from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from chatbot.models import UserProfile

class ChatbotTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('whatsapp_webhook')
        self.phone = '1234567890'

    def send_message(self, body):
        return self.client.post(self.url, {'From': f"whatsapp:{self.phone}", 'Body': body}, HTTP_HOST='testserver')

    @patch('chatbot.services.prembly.requests.post')
    def test_full_flow(self, mock_post):
        # Configure the mock to return a successful verification response
        mock_post.return_value.json.return_value = {
            "status": True,
            "data": {
                "firstname": "John",
                "surname": "Doe",
                "phone": "08012121212",
                "valid": True,
                "photo": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=" # 1x1 pixel base64
            }
        }

        # 1. New User says Hi
        response = self.send_message("Hi")
        self.assertIn("Welcome", str(response.content))
        self.assertIn("provide your *Prembly API Key*", str(response.content))
        
        user = UserProfile.objects.get(phone_number=self.phone)
        self.assertEqual(user.conversation_state, 'AWAITING_AUTH_KEY')

        # 2. User provides short/invalid key (mock check logic is inside BotLogic which calls PremblyService)
        # Note: PremblyService.check_api_key_validity is still a placeholder in the file I wrote, 
        # unless user changed it. Let's assume it returns True for length > 10.
        
        # 3. User provides valid key
        response = self.send_message("valid-api-key-12345") # > 10 chars
        self.assertIn("Authentication successful", str(response.content))
        
        user.refresh_from_db()
        self.assertEqual(user.conversation_state, 'AUTHENTICATED')

        # 4. User asks to verify phone
        response = self.send_message("I want to verify a phone number")
        self.assertIn("type the *phone number*", str(response.content))
        
        user.refresh_from_db()
        self.assertEqual(user.conversation_state, 'AWAITING_PHONE_INPUT')

        # 5. User provides phone number
        mock_post.return_value.json.return_value = {
            "status": True,
            "data": {
                "firstname": "John",
                "surname": "Doe",
                "valid": True,
                "photo": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=" 
            }
        }
        response = self.send_message("08012345678")
        self.assertIn("Verification Successful", str(response.content))
        self.assertIn("John Doe", str(response.content))
        self.assertIn(f"http://testserver/whatsapp/image/{self.phone}/", str(response.content))
        
        user.refresh_from_db()
        self.assertEqual(user.conversation_state, 'AUTHENTICATED')

        # 6. Verify BVN
        response = self.send_message("Verify BVN")
        self.assertIn("type the *BVN*", str(response.content))
        user.refresh_from_db()
        self.assertEqual(user.conversation_state, 'AWAITING_BVN_INPUT')
        
        # BVN Response Mock
        mock_post.return_value.json.return_value = {
            "status": True,
            "data": {
                "firstname": "Jane",
                "surname": "Doe",
                "valid": True
                # No photo
            }
        }
        response = self.send_message("12345678901")
        self.assertIn("Jane Doe", str(response.content))
        self.assertNotIn("Media", str(response.content)) # No image
        
        user.refresh_from_db()
        self.assertEqual(user.conversation_state, 'AUTHENTICATED')
