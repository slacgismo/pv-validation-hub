from django.contrib import admin
from .models import Versions


@admin.register(Versions)
class VersionsAdmin(admin.ModelAdmin):
    list_display = ("id", "python_versions", "cur_worker_version")
    search_fields = ("python_versions", "cur_worker_version")
