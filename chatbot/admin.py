from django.contrib import admin
from .models import Conversation, Message, AIUsage

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'model_name', 'is_pinned', 'created_at', 'updated_at']
    list_filter = ['model_name', 'is_pinned', 'created_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'role', 'content_preview', 'search_used', 'created_at']
    list_filter = ['role', 'search_used', 'created_at']
    search_fields = ['content', 'conversation__user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

    def content_preview(self, obj):
        return obj.content[:60] + "..." if len(obj.content) > 60 else obj.content
    content_preview.short_description = 'Content'


@admin.register(AIUsage)
class AIUsageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'model_name', 'input_tokens', 'output_tokens', 'total_tokens', 'created_at']
    list_filter = ['model_name', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
