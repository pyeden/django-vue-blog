from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Notification.objects.filter(recipient=request.user).select_related(
            "actor", "target_article"
        )[:20]
        unread_count = Notification.objects.filter(
            recipient=request.user, unread=True
        ).count()
        return Response(
            {
                "unread_count": unread_count,
                "results": NotificationSerializer(
                    queryset, many=True, context={"request": request}
                ).data,
            }
        )


class NotificationReadAllView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        updated = Notification.objects.filter(
            recipient=request.user, unread=True
        ).update(unread=False)
        return Response({"updated": updated, "unread_count": 0})


class NotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        notification = Notification.objects.filter(pk=pk, recipient=request.user).first()
        if notification is None:
            return Response({"detail": "通知不存在。"}, status=status.HTTP_404_NOT_FOUND)
        if notification.unread:
            notification.unread = False
            notification.save(update_fields=["unread"])
        return Response(
            NotificationSerializer(notification, context={"request": request}).data
        )
