from django.urls import path
from . import views

urlpatterns = [
    path("webhook", views.whatsapp_webhook, name="whatsapp_webhook"),
    path("image/<str:phone_number>/", views.get_verification_image, name="get_verification_image"),
]
