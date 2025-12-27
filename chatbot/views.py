from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from chatbot.services.bot_logic import BotLogic
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'POST':
        # Get message details
        incoming_msg = request.POST.get('Body', '')
        from_number = request.POST.get('From', '').replace('whatsapp:', '')
        
        if request.scheme and request.get_host():
            base_url = f"{request.scheme}://{request.get_host()}"
        else:
            base_url = "" # Fallback

        # Process message
        bot = BotLogic()
        bot_response = bot.handle_message(from_number, incoming_msg)

        # Create Twilio Response
        resp = MessagingResponse()
        msg = resp.message()

        if isinstance(bot_response, dict):
            msg.body(bot_response.get("text", ""))
            if bot_response.get("has_image"):
                image_url = f"{base_url}/whatsapp/image/{bot_response['phone_number']}/"
                msg.media(image_url)
        else:
            # Fallback for legacy string return (though we updated it)
            msg.body(str(bot_response))

        return HttpResponse(str(resp))
    else:
        return HttpResponse("Only POST requests are accepted.", status=405)

import base64
from django.shortcuts import get_object_or_404
from chatbot.models import UserProfile

def get_verification_image(request, phone_number):
    user = get_object_or_404(UserProfile, phone_number=phone_number)
    if not user.last_verification_image:
        return HttpResponse("No image found", status=404)
    
    try:
        image_data = base64.b64decode(user.last_verification_image)
        return HttpResponse(image_data, content_type="image/jpeg") # Assuming JPEG
    except Exception as e:
        logger.error(f"Error decoding image: {e}")
        return HttpResponse("Error decoding image", status=500)
