from django.urls import path
from .views import AgenteChatAPIView

urlpatterns = [
    path('chat/', AgenteChatAPIView.as_view(), name='agente-chat'),
]
