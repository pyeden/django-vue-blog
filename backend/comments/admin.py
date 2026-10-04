from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "article", "user", "parent", "active", "created")
    list_filter = ("active", "created")
    search_fields = ("body", "user__username", "article__title")
