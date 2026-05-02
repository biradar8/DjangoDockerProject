from django.views.generic import TemplateView

from . import models, services


class BlogIndexView(TemplateView):
    template_name = "blog/post_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_term = self.request.GET.get("q", "")
        category_slug = self.request.GET.get("category", None)

        posts = services.fetch_posts(
            request=self.request,
            limit=10,
            offset=0,
            search=search_term or None,
            category_slug=category_slug or None,
        )

        context["posts"] = posts
        context["categories"] = models.Category.objects.all()
        if search_term:
            context["search_term"] = search_term
        if category_slug:
            context["selected_category"] = category_slug

        return context


class BlogPostDetailView(TemplateView):
    template_name = "blog/post_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        slug = self.kwargs.get("slug")

        post = services.fetch_post_by_slug(
            self.request,
            slug,
        )

        context["post"] = post

        return context
