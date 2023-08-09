from django.urls import path

from goals.apps import GoalsConfig
from goals.views.board import BoardCreateView, BoardListView, BoardView
from goals.views.category import GoalCategoryListView, GoalCategoryCreateView, GoalCategoryView
from goals.views.comment import GoalCommentDetailView, GoalCommentListView, GoalCommentCreateView
from goals.views.goals import GoalListView, GoalCreateView, GoalDetailView

app_name = GoalsConfig.name

urlpatterns = [
    path("board/create", BoardCreateView.as_view(), name='board-create'),
    path("board/list", BoardListView.as_view(), name='board-list'),
    path("board/<int:pk>", BoardView.as_view(), name='board-details'),

    path("goal_category/create", GoalCategoryCreateView.as_view(), name='create-category'),
    path("goal_category/list", GoalCategoryListView.as_view(), name='categories-list'),
    path("goal_category/<int:pk>", GoalCategoryView.as_view(), name='category-details'),

    path("goal/create", GoalCreateView.as_view(), name='create-goal'),
    path("goal/list", GoalListView.as_view(), name='goal-list'),
    path("goal/<int:pk>", GoalDetailView.as_view(), name='goal-detail'),

    path("goal_comment/create", GoalCommentCreateView.as_view(), name='create-comment'),
    path("goal_comment/list", GoalCommentListView.as_view(), name='comments-list'),
    path("goal_comment/<int:pk>", GoalCommentDetailView.as_view(), name='comment-detail'),
]
