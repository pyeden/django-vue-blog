from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.models import Article
from notices.models import Notification

from .models import Comment
from .serializers import CommentCreateSerializer, CommentSerializer


class IsCommentAuthorOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_staff or obj.user_id == request.user.id
        )


class ArticleCommentsView(APIView):
    permission_classes = [permissions.AllowAny]

    def _get_article(self, slug):
        return Article.objects.filter(slug=slug).first()

    def get(self, request, slug):
        article = self._get_article(slug)
        if article is None:
            return Response({"detail": "文章不存在。"}, status=status.HTTP_404_NOT_FOUND)
        roots = (
            Comment.objects.filter(article=article, active=True, parent__isnull=True)
            .select_related("user", "user__profile")
            .prefetch_related("replies__user__profile")
        )
        return Response(CommentSerializer(roots, many=True, context={"request": request}).data)

    def post(self, request, slug):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "请先登录。"}, status=status.HTTP_401_UNAUTHORIZED
            )
        article = self._get_article(slug)
        if article is None:
            return Response({"detail": "文章不存在。"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parent = None
        parent_id = serializer.validated_data.get("parent_id")
        if parent_id:
            parent = Comment.objects.filter(
                pk=parent_id, article=article, active=True
            ).first()
            if parent is None:
                return Response(
                    {"parent_id": ["父评论不存在或不属于该文章。"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Keep the tree two levels deep: reply to a reply -> attach to root.
            if parent.parent_id is not None:
                parent = parent.parent

        comment = Comment.objects.create(
            article=article,
            user=request.user,
            body=serializer.validated_data["body"],
            parent=parent,
        )

        if article.author_id != request.user.id:
            Notification.objects.create(
                recipient=article.author,
                actor=request.user,
                verb="commented",
                target_article=article,
                target_comment=comment,
            )

        return Response(
            CommentSerializer(comment, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class CommentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCommentAuthorOrStaff]
    http_method_names = ["delete"]

    def get_object(self, pk):
        return Comment.objects.filter(pk=pk).first()

    def delete(self, request, pk):
        comment = self.get_object(pk)
        if comment is None:
            return Response({"detail": "评论不存在。"}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, comment)
        comment.active = False
        comment.save(update_fields=["active"])
        return Response(status=status.HTTP_204_NO_CONTENT)
