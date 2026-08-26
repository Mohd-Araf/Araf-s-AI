"""
Memory and Context Management Service for Araf's Assistant.
Retrieves message history from the database and constructs the message list for LLM context.
"""
from typing import List, Dict
from chatbot.models import Conversation, Message
from services.prompt_service import build_system_prompt

def get_conversation_context(
    conversation: Conversation,
    search_context: str = "",
    user_custom_instructions: str = "",
    max_history_messages: int = 15
) -> List[Dict[str, str]]:
    """
    Constructs the full context payload for the AI model, including:
    1. System prompt (with web search grounding + user instructions)
    2. Chronological previous conversation messages (up to max_history_messages)
    """
    # 1. System instruction
    system_prompt = build_system_prompt(
        search_context=search_context,
        user_custom_instructions=user_custom_instructions
    )
    
    context_messages = [{"role": "system", "content": system_prompt}]

    # 2. Fetch past messages in chronological order
    past_messages = conversation.messages.order_by('-created_at')[:max_history_messages]
    past_messages = list(reversed(past_messages))

    for msg in past_messages:
        context_messages.append({
            "role": msg.role,
            "content": msg.content
        })

    return context_messages
