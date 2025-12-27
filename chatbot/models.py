from django.db import models

class UserProfile(models.Model):
    STATE_CHOICES = [
        ('NEW_USER', 'New User'),
        ('AWAITING_AUTH_KEY', 'Awaiting API Key'),
        ('AUTHENTICATED', 'Authenticated'),
        ('AWAITING_VERIFICATION_TYPE', 'Awaiting Verification Type'),
        ('AWAITING_PHONE_INPUT', 'Awaiting Phone Number Input'),
        ('AWAITING_BVN_INPUT', 'Awaiting BVN Input'),
        ('AWAITING_NIN_INPUT', 'Awaiting NIN Input'),
    ]

    phone_number = models.CharField(max_length=20, unique=True)
    prembly_api_key = models.CharField(max_length=255, blank=True, null=True)
    conversation_state = models.CharField(
        max_length=50, 
        choices=STATE_CHOICES, 
        default='NEW_USER'
    )
    last_verification_image = models.TextField(blank=True, null=True)
    last_interaction = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone_number} - {self.conversation_state}"
