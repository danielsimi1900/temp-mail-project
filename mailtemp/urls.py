
from django.urls import path
from . import views

urlpatterns = [
    path('webhook/inbound/', views.inbound_webhook, name='webhook_inbound'),
    path('api/inbox/<str:local>/', views.inbox_list, name='inbox_list'),
    path('api/message/<str:msgid>/', views.message_detail, name='message_detail'),
    path('api/generate/', views.generate_address, name='generate_address'),
]
