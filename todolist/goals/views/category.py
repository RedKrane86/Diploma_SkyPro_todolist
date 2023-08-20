from django.db import transaction
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from goals.models import GoalCategory, Goal
from goals.permission_classes import GoalCategoryPermissions
from goals.serializers import GoalCreateCategorySerializer, GoalCategorySerializer


class GoalCategoryCreateView(CreateAPIView):
    """
    Представление для создания категории
    """
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCreateCategorySerializer


class GoalCategoryListView(ListAPIView):
    """
    Представление для отображения всех категорий
    """
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermissions]
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]

    def get_queryset(self):
        """
        Ответ фильтруется по списку участников
        """
        return GoalCategory.objects.filter(
            board__participants__user=self.request.user,
            is_deleted=False,
        )


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    """
    Представление для детального просмотра, обновления и удаления категории
    """
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermissions]

    def get_queryset(self):
        """
        Удаленные категории не отображаются
        """
        return GoalCategory.objects.filter(is_deleted=False)

    def perform_destroy(self, instance: GoalCategory):
        """
        Категория не удаляется, а архивируется
        Пользователь их не видит, но видит администратор через админ панель
        """
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.goal_set.update(status=Goal.Status.archived)
            return instance
