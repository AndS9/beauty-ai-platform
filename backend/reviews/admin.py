from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment", "client", "master", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("client__email", "master__user__email", "comment")
