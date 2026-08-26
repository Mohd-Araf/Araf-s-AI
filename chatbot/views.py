import json
import logging
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
    ChatRequestSerializer
)
from services.search_service import should_search_web, search_web
from services.memory_service import get_conversation_context
from services.ai_service import stream_ai_response

logger = logging.getLogger(__name__)

class ConversationListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        conversations = Conversation.objects.filter(user=request.user)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        title = request.data.get('title', 'New Chat')
        model_name = request.data.get('model_name', 'gemini-2.5-flash')
        conversation = Conversation.objects.create(
            user=request.user,
            title=title,
            model_name=model_name
        )
        serializer = ConversationDetailSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConversationDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
        serializer = ConversationDetailSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
        if 'title' in request.data:
            conversation.title = request.data['title'].strip()
        if 'is_pinned' in request.data:
            conversation.is_pinned = bool(request.data['is_pinned'])
        conversation.save()
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
        conversation.delete()
        return Response({"message": "Conversation deleted successfully"}, status=status.HTTP_200_OK)


class ChatStreamAPIView(APIView):
    """
    Server-Sent Events (SSE) streaming chat endpoint.
    Accepts user message, checks web search, saves history, and streams tokens.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        conv_id = serializer.validated_data.get('conversation_id')
        user_message_text = serializer.validated_data['message'].strip()
        manual_search = serializer.validated_data.get('enable_web_search')
        selected_model = serializer.validated_data.get('model', 'gemini-3.6-flash')

        # 1. Get or create conversation
        if conv_id:
            conversation = get_object_or_404(Conversation, pk=conv_id, user=user)
        else:
            # Auto-title from first message (first 30 chars)
            auto_title = user_message_text[:30] + ("..." if len(user_message_text) > 30 else "")
            conversation = Conversation.objects.create(
                user=user,
                title=auto_title,
                model_name=selected_model
            )

        # 2. Check and perform web search if needed
        is_search_needed = should_search_web(user_message_text, manual_override=manual_search)
        search_context = ""
        citations = []

        if is_search_needed:
            search_context, citations = search_web(user_message_text, max_results=4)

        # 3. Save User Message
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message_text,
            search_used=is_search_needed,
            citations=citations
        )

        # Update conversation title if default
        if conversation.title == 'New Chat' and conversation.messages.count() <= 2:
            conversation.title = user_message_text[:30] + ("..." if len(user_message_text) > 30 else "")
            conversation.save()

        # 4. Build context payload
        custom_instructions = ""
        if hasattr(user, 'profile'):
            custom_instructions = user.profile.custom_system_prompt

        messages_context = get_conversation_context(
            conversation=conversation,
            search_context=search_context,
            user_custom_instructions=custom_instructions
        )

        # 5. Generator for SSE Streaming
        def event_stream():
            full_response_chunks = []
            
            # Send initial metadata (conversation ID, citations)
            init_payload = {
                "type": "init",
                "conversation_id": conversation.id,
                "conversation_title": conversation.title,
                "search_used": is_search_needed,
                "citations": citations,
            }
            yield f"data: {json.dumps(init_payload)}\n\n"

            # Stream chunks from AI service
            try:
                for chunk in stream_ai_response(messages_context, model=selected_model):
                    if chunk:
                        full_response_chunks.append(chunk)
                        chunk_payload = {
                            "type": "chunk",
                            "chunk": chunk
                        }
                        yield f"data: {json.dumps(chunk_payload)}\n\n"
            except Exception as e:
                err_payload = {"type": "error", "error": str(e)}
                yield f"data: {json.dumps(err_payload)}\n\n"

            # 6. Save Assistant response to database upon completion
            full_content = "".join(full_response_chunks)
            if full_content:
                assistant_message = Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=full_content,
                    search_used=is_search_needed,
                    citations=citations
                )
                done_payload = {
                    "type": "done",
                    "message_id": assistant_message.id,
                    "created_at": assistant_message.created_at.isoformat()
                }
                yield f"data: {json.dumps(done_payload)}\n\n"

        response = StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response


class SearchAPIView(APIView):
    """
    Direct web search test endpoint.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({"error": "Search query parameter 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        context_str, citations = search_web(query, max_results=5)
        return Response({
            "query": query,
            "citations": citations,
            "context_preview": context_str
        }, status=status.HTTP_200_OK)
