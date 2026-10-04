from django.contrib import admin

from .models import Article, ArticleColumn, ArticleLike


@admin.register(ArticleColumn)
class ArticleColumnAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "column", "likes", "total_views", "created")
    list_filter = ("column", "created", "author")
    search_fields = ("title", "body", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("body_html", "total_views", "likes", "created", "updated")
    date_hierarchy = "created"


@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "created")
    search_fields = ("article__title", "user__username")
