"""
Automated Verification Suite for Araf's Assistant
Tests all 10-Day Milestones: Models, Auth, Services, Search, Memory, and SSE Streaming.
"""
import os
import sys
import io
import django

# Ensure stdout supports UTF-8 on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from chatbot.models import Conversation, Message
from services.search_service import should_search_web, search_web
from services.prompt_service import build_system_prompt
from services.memory_service import get_conversation_context
from services.ai_service import stream_ai_response

def run_tests():
    print("=" * 60)
    print(">> Running Verification Tests for Araf's Assistant")
    print("=" * 60)

    client = APIClient()

    # Test 1: User Registration
    print("\n[Test 1] Testing User Registration...")
    User.objects.filter(username="test_araf").delete()
    reg_res = client.post('/api/v1/auth/register/', {
        "username": "test_araf",
        "email": "test_araf@example.com",
        "password": "Password123!",
        "first_name": "Araf"
    }, format='json')
    assert reg_res.status_code == 201, f"Registration failed: {reg_res.data}"
    token = reg_res.data['token']
    print("[PASS] User Registration OK (Token received)")

    # Test 2: User Login
    print("\n[Test 2] Testing User Login...")
    login_res = client.post('/api/v1/auth/login/', {
        "username": "test_araf",
        "password": "Password123!"
    }, format='json')
    assert login_res.status_code == 200, f"Login failed: {login_res.data}"
    print("[PASS] User Login OK")

    # Set auth header
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    # Test 3: Authenticated User Profile
    print("\n[Test 3] Testing GET /api/v1/auth/me/...")
    me_res = client.get('/api/v1/auth/me/')
    assert me_res.status_code == 200, f"Get profile failed: {me_res.data}"
    assert me_res.data['username'] == 'test_araf'
    print(f"[PASS] User Profile verified: {me_res.data['username']}")

    # Test 4: Conversation Creation
    print("\n[Test 4] Testing Conversation Creation...")
    conv_res = client.post('/api/v1/chat/conversations/', {
        "title": "Django & AI Architecture Discussion"
    }, format='json')
    assert conv_res.status_code == 201, f"Conversation creation failed: {conv_res.data}"
    conv_id = conv_res.data['id']
    print(f"[PASS] Conversation created (ID: {conv_id})")

    # Test 5: Search Service & Intent Detector
    print("\n[Test 5] Testing Web Search Service & Trigger Heuristics...")
    assert should_search_web("FastAPI latest version in 2026") == True
    assert should_search_web("ভাই পাইথনে লিস্ট কী?") == False
    print("[PASS] Search heuristic detection OK")

    # Test 6: Prompt & Memory Service
    print("\n[Test 6] Testing Multilingual Prompt & Memory Context...")
    conv = Conversation.objects.get(id=conv_id)
    Message.objects.create(conversation=conv, role='user', content='Django কী?')
    Message.objects.create(conversation=conv, role='assistant', content='Django হলো Python এর একটি জনপ্রিয় ফ্রেমওয়ার্ক।')

    context = get_conversation_context(conversation=conv, search_context="Example Grounding Data")
    assert len(context) >= 3  # system + 2 messages
    assert "Araf's Assistant" in context[0]['content']
    print("[PASS] Multilingual Prompt & Context Memory OK")

    # Test 7: AI Streaming Response
    print("\n[Test 7] Testing AI Stream Generator (Multilingual + Fallback/Gemini)...")
    chunks = list(stream_ai_response(context))
    full_output = "".join(chunks)
    assert len(full_output) > 10
    print(f"[PASS] AI Stream Output ({len(chunks)} chunks generated)")

    # Test 8: SSE Chat Streaming API Endpoint
    print("\n[Test 8] Testing POST /api/v1/chat/stream/ (SSE Endpoint)...")
    stream_res = client.post('/api/v1/chat/stream/', {
        "conversation_id": conv_id,
        "message": "ভাই Django authentication কীভাবে কাজ করে?",
        "enable_web_search": False
    }, format='json')
    assert stream_res.status_code == 200, f"Chat stream failed: {stream_res.status_code}"
    
    # Collect streamed content
    stream_content = b"".join(stream_res.streaming_content).decode('utf-8')
    assert "data: " in stream_content
    print("[PASS] SSE Stream HTTP Response OK")

    # Test 9: Conversation Messages Persistence
    print("\n[Test 9] Verifying Message Persistence in Database...")
    detail_res = client.get(f'/api/v1/chat/conversations/{conv_id}/')
    assert detail_res.status_code == 200
    assert len(detail_res.data['messages']) >= 3
    print(f"[PASS] Database Persistence verified ({len(detail_res.data['messages'])} messages stored)")

    print("\n" + "=" * 60)
    print(">> ALL 9 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
