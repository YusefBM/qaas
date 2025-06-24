from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count
from django.utils.html import format_html

from user.domain.user import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
        "quizzes_created_count",
        "participations_count",
    ]
    list_filter = ["is_staff", "is_superuser", "is_active", "date_joined", "last_login"]
    search_fields = ["username", "email", "first_name", "last_name"]
    readonly_fields = ["id", "date_joined", "last_login"]
    date_hierarchy = "date_joined"

    fieldsets = (
        ("Basic Information", {"fields": ("id", "username", "email", "first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
                "classes": ("collapse",),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined"), "classes": ("collapse",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            quiz_count=Count("quizzes", distinct=True), participation_count=Count("quiz_participations", distinct=True)
        )

    def quizzes_created_count(self, obj):
        count = getattr(obj, "quiz_count", 0)
        if count > 0:
            url = f"/admin/quiz/quiz/?creator__id__exact={obj.id}"
            return format_html('<a href="{}">{} quiz{}</a>', url, count, "s" if count != 1 else "")
        return count

    quizzes_created_count.short_description = "Quizzes Created"
    quizzes_created_count.admin_order_field = "quiz_count"

    def participations_count(self, obj):
        count = getattr(obj, "participation_count", 0)
        if count > 0:
            url = f"/admin/quiz/participation/?participant__id__exact={obj.id}"
            return format_html('<a href="{}">{} participation{}</a>', url, count, "s" if count != 1 else "")
        return count

    participations_count.short_description = "Quiz Participations"
    participations_count.admin_order_field = "participation_count"
