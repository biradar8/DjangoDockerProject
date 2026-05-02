import random

from blog.models import Category, Post
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Generate realistic dummy posts"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="Number of posts to create",
        )
        parser.add_argument(
            "--username",
            type=str,
            default="nexg",
            help="Username for post author",
        )

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database with random posts...")
        count = kwargs["count"]
        username = kwargs["username"]

        # 1. User
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@localhost.com", "is_staff": True},
        )

        # 2. Categories
        cat_names = ["Science", "Technology", "Tutorials", "News", "GraphQL"]
        categories = [
            Category.objects.get_or_create(
                name=name,
                defaults={
                    "slug": slugify(name),
                    "created_by": user,
                    "updated_by": user,
                },
            )[0]
            for name in cat_names
        ]

        # 3. Generate posts
        posts = []
        for i in range(count):
            title = fake.sentence(nb_words=6)

            body = "".join(
                f"<p>{fake.paragraph(nb_sentences=10)}</p>"
                for _ in range(random.randint(2, 5))
            )

            posts.append(
                Post(
                    title=title,
                    title_slug=f"{slugify(title)}-{i}",
                    body=body,
                    category=random.choice(categories),
                    status=Post.Status.PUBLISHED,
                    created_by=user,
                    updated_by=user,
                )
            )

        Post.objects.bulk_create(posts)

        self.stdout.write(self.style.SUCCESS("Done seeding posts!"))
