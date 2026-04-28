from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE

from .models import Category, Post


class BaseModelAdmin(admin.ModelAdmin):
    # What shows up in the table list view
    list_display = ("__str__", "is_active", "created_at", "created_by")

    # What you can filter by in the right sidebar
    list_filter = ("is_active", "created_at", "created_by")

    # Audit fields should be visible but not editable
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")

    # Base autocomplete fields
    autocomplete_fields = ()

    def _get_foreign_key_fields(self):
        """Helper method to retrieve all ForeignKey field names dynamically."""
        return [
            f.name
            for f in self.model._meta.get_fields()
            if isinstance(f, models.ForeignKey)
        ]

    def get_list_filter(self, request):
        """Dynamically append ForeignKey fields to list_filter."""
        filters = list(super().get_list_filter(request) or [])
        fk_fields = self._get_foreign_key_fields()

        for fk in fk_fields:
            if fk not in filters:
                filters.append(fk)

        return tuple(filters)

    def get_autocomplete_fields(self, request):
        """Dynamically append ForeignKey fields to autocomplete_fields."""
        autocomplete = list(super().get_autocomplete_fields(request) or [])
        fk_fields = self._get_foreign_key_fields()

        for fk in fk_fields:
            if fk not in autocomplete:
                autocomplete.append(fk)

        return tuple(autocomplete)

    def get_fieldsets(self, request, obj=None):
        """
        Dynamically creates fieldsets.
        Places model-specific fields in the first section
        and audit fields in a collapsed second section.
        """
        # 1. Get all fields defined in the model
        all_fields = [
            f.name
            for f in self.model._meta.get_fields()
            if not f.is_relation or f.many_to_one
        ]

        # 2. Separate "main" fields from "audit" fields
        # We exclude ID and the audit fields from the main section
        main_fields = [
            f for f in all_fields if f not in self.readonly_fields and f != "id"
        ]

        return [
            ("General Information", {"fields": main_fields}),
            (
                "History",
                {
                    "classes": ("collapse",),  # This makes the section collapsible
                    "description": "Information about when and by whom this record was created/updated.",
                    "fields": self.readonly_fields,
                },
            ),
        ]


class CategoryAdmin(BaseModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


class PostAdmin(BaseModelAdmin):
    prepopulated_fields = {"title_slug": ("title",)}
    list_display = BaseModelAdmin.list_display + ("category", "status")
    formfield_overrides = {models.TextField: {"widget": TinyMCE()}}

    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
