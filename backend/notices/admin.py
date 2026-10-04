from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "actor", "verb", "target_article", "unread", "created")
    list_filter = ("unread", "verb", "created")
    search_fields = ("recipient__username", "actor__username", "verb")
