from typing import Any

from django.db.models import Q, F
from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request

from goals.models import BoardParticipant, Board, GoalCategory, Goal, GoalComments


class BoardPermissions(permissions.IsAuthenticated):
    """
    Доступ к доске.
        - Если пользователь не авторизован, то запретить доступ
        - Если пользователь авторизован, но не является владельцем, то разрешить только просмотр
        - Если авторизован и является владельцем, то разрешить все доступные действия
    """
    def has_object_permission(self, request: Request, view: GenericAPIView, obj: Board) -> bool:
        _filters: dict[str, Any] = {'user': request.user, 'board': obj}
        if request.method not in permissions.SAFE_METHODS:
            _filters['role'] = BoardParticipant.Role.owner

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalCategoryPermissions(permissions.IsAuthenticated):
    """
    Доступ к категории целей.
        - Если пользователь не авторизован, то запретить доступ
        - Если пользователь авторизован, но не является владельцем или редактором, то разрешить только просмотр
        - Если авторизован является владельцем или редактором, то разрешить все доступные действия
    """

    def has_object_permission(self, request: Request, view: GenericAPIView, obj: GoalCategory) -> bool:
        _filters: dict[str, Any] = {'user': request.user, 'board': obj.board}
        if request.method not in permissions.SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalPermissions(permissions.IsAuthenticated):
    """
    Доступ к целям.
        - Если пользователь не авторизован, то запретить доступ
        - Если пользователь авторизован, но не является владельцем или редактором, то разрешить только просмотр
        - Если авторизован является владельцем или редактором, то разрешить все доступные действия
    """

    def has_object_permission(self, request: Request, view: GenericAPIView, obj: Goal) -> bool:
        _filters: dict[str, Any] = {'user': request.user, 'board': obj.category.board}
        if request.method not in permissions.SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]

        return BoardParticipant.objects.filter(**_filters).exists()


class GoalCommentPermissions(permissions.IsAuthenticated):
    """
    Доступ к комментариям целей.
        - Если пользователь не авторизован, то запретить доступ
        - Если пользователь авторизован, но не является владельцем, то разрешить только просмотр
        - Если авторизован является владельцем, то разрешить все доступные действия
    """
    def has_object_permission(self, request: Request, view: GenericAPIView, obj: GoalComments) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.user

