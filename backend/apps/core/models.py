from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import json


class AuditLog(models.Model):
    """Система аудита для отслеживания всех изменений"""
    ACTION_CHOICES = [
        ('created', 'Создано'),
        ('updated', 'Обновлено'),
        ('deleted', 'Удалено'),
        ('viewed', 'Просмотрено'),
    ]
    
    action = models.CharField(max_length=100, choices=ACTION_CHOICES)
    actor = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_logs')
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Данные до изменения
    old_data = models.JSONField(null=True, blank=True)
    # Данные после изменения
    new_data = models.JSONField(null=True, blank=True)
    
    path = models.CharField(max_length=255, blank=True)
    method = models.CharField(max_length=10, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['actor', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.created_at} - {self.get_action_display()} by {self.actor or 'Unknown'}"



