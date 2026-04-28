from django.conf import settings
from django.db import models
from django.utils.text import slugify

from config.middleware import get_current_user


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
    )

    def save(self, *args, **kwargs):
        user = get_current_user()

        if user and getattr(user, "is_authenticated", False):
            if not self.pk:
                self.created_by = user
            self.updated_by = user

        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"
        ARCHIVED = "AR", "Archived"

    title = models.CharField(max_length=250)
    title_slug = models.SlugField(unique=True, blank=True, max_length=250)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="posts"
    )
    body = models.TextField()
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.title_slug:
            self.title_slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
