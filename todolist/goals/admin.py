from django.contrib import admin

from goals.models import GoalCategory, Goal


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    """
    Класс админ панели для категорий
    """
    list_display = ("title", "user", "created", "updated")
    search_fields = ("title", "user")


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    """
    Класс админ панели для целей
    """
    list_display = ("title", "user", "created", "updated")
    search_fields = ["title"]
