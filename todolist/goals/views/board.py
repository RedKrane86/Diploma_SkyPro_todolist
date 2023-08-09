from django.db import transaction
from rest_framework import permissions, filters
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
from rest_framework.pagination import LimitOffsetPagination

from goals.models import Board, Goal
from goals.permission_classes import BoardPermissions
from goals.serializers import BoardSerializer, BoardCreateSerializer, BoardListSerializer


class BoardCreateView(CreateAPIView):
    """
    Представление создания доски
    """
    serializer_class = BoardCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class BoardListView(ListAPIView):
    """
    Представление для отображения всех досок
    """
    serializer_class = BoardListSerializer
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    ordering = ['title']

    def get_queryset(self):
        """
        Фильтрация ответа идет через фильтр participants__user
        """
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)


class BoardView(RetrieveUpdateDestroyAPIView):
    """
    Представление для детального просмотра, изменения
    и удаления(архивации) доски
    """

    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self):
        """
        Фильтрация ответа идет через фильтр participants__user
        """
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance: Board):
        """
        При удалении доски помечаем ее как is_deleted, архивируем категории, обновляем статус целей
        """
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)
        return instance
