from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, filters
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView

from goals.models import GoalComments
from goals.permission_classes import GoalCommentPermissions
from goals.serializers import GoalCommentCreateSerializer, GoalCommentSerializer


class GoalCommentCreateView(CreateAPIView):
    model = GoalComments
    serializer_class = GoalCommentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class GoalCommentListView(ListAPIView):
    serializer_class = GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated, GoalCommentPermissions]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal']
    ordering = ['-created']

    def get_queryset(self):
        return GoalComments.objects.filter(
            goal__category__board__participants__user=self.request.user
        )


class GoalCommentDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated, GoalCommentPermissions]

    def get_queryset(self):
        return GoalComments.objects.select_relatied('user').filter(
            goal__category__board__participants__user=self.request.user
        )
