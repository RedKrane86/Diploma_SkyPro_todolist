from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from goals.filters import GoalDateFilter
from goals.models import Goal
from goals.permission_classes import GoalPermissions
from goals.serializers import GoalSerializer, GoalCreateSerializer


class GoalCreateView(CreateAPIView):
    """
    Представление для создания целей
    """
    model = Goal
    serializer_class = GoalCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class GoalListView(ListAPIView):
    """
    Представление для отображения всех целей.
    Сортируется по названию
    Поиск происходит по названию и описанию
    """
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalDateFilter
    ordering_fields = ['title', 'description']
    ordering = ['title']
    search_fields = ['title', 'description']

    def get_queryset(self):
        """
        Ответ фильтруется по списку участников
        Удаленные(архивированные) цели не видны
        """
        return Goal.objects.filter(
            category__board__participants__user=self.request.user,
            category__is_deleted=False
        ).exclude(
            status=Goal.Status.archived
        )


class GoalDetailView(RetrieveUpdateDestroyAPIView):
    """
    Представление для детального просмотра, обновления и удаления(архивации) целей
    """
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]
    serializer_class = GoalSerializer

    def get_queryset(self):
        """
        Удаленные(архивированные) цели не видны
        """
        return Goal.objects.filter(
            category__is_deleted=False
        ).exclude(
            status=Goal.Status.archived)

    def perform_destroy(self, instance: Goal) -> None:
        """
        Цель не удаляется, а архивируется
        Пользователь их не видит, но видит администратор через админ панель
        """
        instance.status = Goal.Status.archived
        instance.save()
