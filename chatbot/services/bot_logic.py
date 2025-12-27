from chatbot.models import UserProfile
from chatbot.services.prembly import PremblyService

class BotLogic:
    def handle_message(self, phone_number, message_body):
        user, created = UserProfile.objects.get_or_create(phone_number=phone_number)
        message_body = message_body.strip()
        
        if created:
            user.conversation_state = 'NEW_USER'
            user.save()

        state = user.conversation_state
        response = "" # Default string response

        if state == 'NEW_USER':
            response = (
                "Welcome to the Prembly Verification Bot! \U0001F916\n"
                "I can help you verify identities using your Prembly account.\n\n"
                "To get started, please provide your *Prembly API Key* so I can authenticate you."
            )
            user.conversation_state = 'AWAITING_AUTH_KEY'
            user.save()

        elif state == 'AWAITING_AUTH_KEY':
            if len(message_body) > 10: 
                svc = PremblyService(api_key=message_body)
                if svc.check_api_key_validity(message_body):
                    user.prembly_api_key = message_body
                    user.conversation_state = 'AUTHENTICATED'
                    user.save()
                    response = (
                        "Authentication successful! \U00002705\n\n"
                        "You can now ask me to verify identities.\n"
                        "Try saying:\n"
                        "- *'Verify phone number'*\n"
                        "- *'Verify BVN'*\n"
                        "- *'Verify NIN'*"
                    )
                else:
                    response = "That API Key seems invalid. Please try again."
            else:
                response = "Please enter a valid API Key."

        elif state == 'AUTHENTICATED':
            msg_lower = message_body.lower()
            if 'phone' in msg_lower and 'verify' in msg_lower:
                response = "Sure, please type the *phone number* you want to verify."
                user.conversation_state = 'AWAITING_PHONE_INPUT'
                user.save()
            elif 'bvn' in msg_lower and 'verify' in msg_lower:
                response = "Sure, please type the *BVN* you want to verify."
                user.conversation_state = 'AWAITING_BVN_INPUT'
                user.save()
            elif 'nin' in msg_lower and 'verify' in msg_lower:
                response = "Sure, please type the *NIN* you want to verify."
                user.conversation_state = 'AWAITING_NIN_INPUT'
                user.save()
            elif 'logout' in msg_lower:
                user.prembly_api_key = None
                user.conversation_state = 'NEW_USER'
                user.save()
                response = "You have been logged out."
            else:
                response = (
                    "I didn't quite catch that. \n"
                    "Try saying: *'Verify phone'*, *'Verify BVN'*, *'Verify NIN'* or *'Logout'*."
                )

        elif state in ['AWAITING_PHONE_INPUT', 'AWAITING_BVN_INPUT', 'AWAITING_NIN_INPUT']:
            target_number = message_body
            svc = PremblyService(api_key=user.prembly_api_key)
            
            result = {}
            if state == 'AWAITING_PHONE_INPUT':
                result = svc.verify_phone_number(target_number)
            elif state == 'AWAITING_BVN_INPUT':
                result = svc.verify_bvn(target_number)
            elif state == 'AWAITING_NIN_INPUT':
                result = svc.verify_nin(target_number)

            return self._process_verification_result(user, result, target_number)

        return {"text": response}

    def _process_verification_result(self, user, result, target_number):
        if result.get('status'):
            data = result.get('data', {})
            # Save image if present
            photo_base64 = data.get('photo') or data.get('image') # Handle potential variations
            if photo_base64:
                user.last_verification_image = photo_base64
                user.save()
            
            # Construct name differently if needed, but assuming similar structure
            name = f"{data.get('firstname', '')} {data.get('surname', '')} {data.get('lastname', '')}".strip()
            
            response_text = (
                f"\U00002705 Verification Successful for {target_number}:\n"
                f"Name: {name}\n"
                f"Valid: {data.get('valid')}"
            )
            
            user.conversation_state = 'AUTHENTICATED'
            user.save()
            return {
                "text": response_text,
                "has_image": bool(photo_base64),
                "phone_number": user.phone_number
            }
        else:
            response_text = f"\U0000274C Verification Failed: {result.get('message')}"
            
            user.conversation_state = 'AUTHENTICATED'
            user.save()
            return {"text": response_text}
