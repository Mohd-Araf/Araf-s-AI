from django.urls import path
from .views import (
    ConversationListCreateAPIView,
    ConversationDetailAPIView,
    ChatStreamAPIView,
    SearchAPIView
)

urlpatterns = [
    path('conversations/', ConversationListCreateAPIView.as_view(), name='conversation_list_create'),
    path('conversations/<int:pk>/', ConversationDetailAPIView.as_view(), name='conversation_detail'),
    path('stream/', ChatStreamAPIView.as_view(), name='chat_stream'),
    path('search/', SearchAPIView.as_view(), name='web_search_direct'),
]
