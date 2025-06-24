from django.contrib import admin
from django.db.models import Avg, Count
from django.urls import reverse
from django.utils.html import format_html

from quiz.domain.invitation.invitation import Invitation
from quiz.domain.participation.answer_submission import AnswerSubmission
from quiz.domain.participation.participation import Participation
from quiz.domain.quiz.answer import Answer
from quiz.domain.quiz.question import Question
from quiz.domain.quiz.quiz import Quiz


# =============================================================================
# INLINE CLASSES
# =============================================================================


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3
    fields = ["text", "is_correct", "order"]
    ordering = ["order"]


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ["text", "order", "points"]
    ordering = ["order"]
    show_change_link = True


class InvitationInline(admin.TabularInline):
    model = Invitation
    extra = 0
    readonly_fields = ["invited_at", "accepted_at"]
    fields = ["invited", "inviter", "accepted_at", "invited_at"]


class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 0
    readonly_fields = ["created_at", "completed_at", "participation_status_display"]
    fields = ["participant", "invitation", "score", "completed_at", "participation_status_display", "created_at"]

    def participation_status_display(self, obj):
        if obj and obj.pk:
            return obj.status
        return "Unknown"

    participation_status_display.short_description = "Status"


class AnswerSubmissionInline(admin.TabularInline):
    model = AnswerSubmission
    extra = 0
    readonly_fields = ["submitted_at", "is_correct_display"]
    fields = ["question", "selected_answer", "is_correct_display", "submitted_at"]

    def is_correct_display(self, obj):
        if obj and obj.pk:
            return obj.is_correct
        return False

    is_correct_display.boolean = True
    is_correct_display.short_description = "Correct"


# =============================================================================
# MAIN ADMIN CLASSES
# =============================================================================


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "creator",
        "total_questions_display",
        "total_participants_display",
        "average_score_display",
        "created_at",
        "updated_at",
    ]
    list_filter = ["created_at", "updated_at", "creator"]
    search_fields = [
        "title",
        "description",
        "creator__username",
        "creator__email",
        "creator__first_name",
        "creator__last_name",
    ]
    readonly_fields = ["id", "created_at", "updated_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Basic Information", {"fields": ("id", "title", "description", "creator")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    inlines = [QuestionInline, InvitationInline, ParticipationInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs.select_related("creator")
            .prefetch_related("questions", "participations", "invitations")
            .annotate(
                avg_score=Avg("participations__score"),
                participation_count=Count("participations"),
                question_count=Count("questions"),
            )
        )

    def total_questions_display(self, obj):
        return getattr(obj, "question_count", obj.total_questions)

    total_questions_display.short_description = "Questions"
    total_questions_display.admin_order_field = "question_count"

    def total_participants_display(self, obj):
        return getattr(obj, "participation_count", obj.total_participants)

    total_participants_display.short_description = "Participants"
    total_participants_display.admin_order_field = "participation_count"

    def average_score_display(self, obj):
        avg_score = getattr(obj, "avg_score", None)
        if avg_score is not None:
            return f"{avg_score:.1f}"
        return "N/A"

    average_score_display.short_description = "Avg Score"
    average_score_display.admin_order_field = "avg_score"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text_truncated", "quiz", "order", "points", "answer_count_display", "created_at"]
    list_filter = ["quiz", "points", "created_at"]
    search_fields = ["text", "quiz__title", "quiz__creator__username"]
    readonly_fields = ["id", "created_at"]
    ordering = ["quiz", "order"]

    fieldsets = (
        ("Basic Information", {"fields": ("id", "quiz", "text", "order", "points")}),
        ("Timestamps", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    inlines = [AnswerInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs.select_related("quiz", "quiz__creator")
            .prefetch_related("answers")
            .annotate(answer_count=Count("answers"))
        )

    def text_truncated(self, obj):
        return obj.text[:80] + ("..." if len(obj.text) > 80 else "")

    text_truncated.short_description = "Question Text"

    def answer_count_display(self, obj):
        return getattr(obj, "answer_count", obj.answers.count())

    answer_count_display.short_description = "Answers"
    answer_count_display.admin_order_field = "answer_count"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["text_truncated", "question_truncated", "quiz_title", "is_correct", "order"]
    list_filter = ["is_correct", "question__quiz", "question__quiz__creator"]
    search_fields = ["text", "question__text", "question__quiz__title"]
    readonly_fields = ["id"]
    ordering = ["question__quiz", "question__order", "order"]

    fieldsets = (("Basic Information", {"fields": ("id", "question", "text", "is_correct", "order")}),)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("question", "question__quiz", "question__quiz__creator")

    def text_truncated(self, obj):
        return obj.text[:50] + ("..." if len(obj.text) > 50 else "")

    text_truncated.short_description = "Answer Text"

    def question_truncated(self, obj):
        return obj.question.text[:50] + ("..." if len(obj.question.text) > 50 else "")

    question_truncated.short_description = "Question"

    def quiz_title(self, obj):
        return obj.question.quiz.title

    quiz_title.short_description = "Quiz"


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ["quiz", "invited", "inviter", "invitation_status", "invited_at", "accepted_at"]
    list_filter = ["invited_at", "accepted_at", "quiz", "inviter"]
    search_fields = [
        "invited__username",
        "invited__email",
        "invited__first_name",
        "invited__last_name",
        "inviter__username",
        "inviter__email",
        "quiz__title",
    ]
    readonly_fields = ["id", "invited_at", "accepted_at", "is_accepted_display"]
    date_hierarchy = "invited_at"

    fieldsets = (
        ("Basic Information", {"fields": ("id", "quiz", "invited", "inviter")}),
        ("Status", {"fields": ("is_accepted_display",)}),
        ("Timestamps", {"fields": ("invited_at", "accepted_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("quiz", "invited", "inviter")

    def invitation_status(self, obj):
        if obj.is_accepted():
            return format_html('<span style="color: green;">✓ Accepted</span>')
        else:
            return format_html('<span style="color: orange;">⏳ Pending</span>')

    invitation_status.short_description = "Status"

    def is_accepted_display(self, obj):
        return obj.is_accepted() if obj and obj.pk else False

    is_accepted_display.boolean = True
    is_accepted_display.short_description = "Accepted"


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = [
        "participant",
        "quiz",
        "participation_status_display",
        "score",
        "invitation_link",
        "created_at",
        "completed_at",
    ]
    list_filter = ["created_at", "completed_at", "quiz", "quiz__creator"]
    search_fields = [
        "participant__username",
        "participant__email",
        "participant__first_name",
        "participant__last_name",
        "quiz__title",
        "quiz__creator__username",
    ]
    readonly_fields = ["id", "created_at", "completed_at", "participation_status_display"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Basic Information", {"fields": ("id", "quiz", "participant", "invitation")}),
        ("Progress", {"fields": ("participation_status_display", "score", "completed_at")}),
        ("Timestamps", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    inlines = [AnswerSubmissionInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("participant", "quiz", "quiz__creator", "invitation").prefetch_related(
            "answer_submissions"
        )

    def participation_status_display(self, obj):
        status = obj.status
        if status == "completed":
            return format_html('<span style="color: green;">✓ Completed</span>')
        else:
            return format_html('<span style="color: orange;">⏳ In Progress</span>')

    participation_status_display.short_description = "Status"

    def invitation_link(self, obj):
        if obj.invitation:
            url = reverse("admin:quiz_invitation_change", args=[obj.invitation.id])
            return format_html('<a href="{}">View Invitation</a>', url)
        return "No invitation"

    invitation_link.short_description = "Invitation"


@admin.register(AnswerSubmission)
class AnswerSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        "participation",
        "question_truncated",
        "selected_answer_truncated",
        "is_correct_display",
        "submitted_at",
    ]
    list_filter = ["selected_answer__is_correct", "submitted_at", "participation__quiz", "participation__quiz__creator"]
    search_fields = [
        "participation__participant__username",
        "participation__participant__email",
        "participation__quiz__title",
        "question__text",
        "selected_answer__text",
    ]
    readonly_fields = ["id", "submitted_at", "is_correct_display"]
    date_hierarchy = "submitted_at"

    fieldsets = (
        ("Basic Information", {"fields": ("id", "participation", "question", "selected_answer")}),
        ("Result", {"fields": ("is_correct_display", "submitted_at")}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "participation", "participation__participant", "participation__quiz", "question", "selected_answer"
        )

    def question_truncated(self, obj):
        return obj.question.text[:50] + ("..." if len(obj.question.text) > 50 else "")

    question_truncated.short_description = "Question"

    def selected_answer_truncated(self, obj):
        return obj.selected_answer.text[:30] + ("..." if len(obj.selected_answer.text) > 30 else "")

    selected_answer_truncated.short_description = "Selected Answer"

    def is_correct_display(self, obj):
        return obj.is_correct

    is_correct_display.boolean = True
    is_correct_display.short_description = "Correct"


# =============================================================================
# ADMIN SITE CUSTOMIZATION
# =============================================================================

admin.site.site_header = "Quiz Management System"
admin.site.site_title = "Quiz Admin"
admin.site.index_title = "Welcome to Quiz Administration"
