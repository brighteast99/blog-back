from django.db.models import Q
from django_filters import CharFilter, FilterSet, NumberFilter

from blog.core.errors import PermissionDeniedError
from blog.core.models import Category, Post


class PostFilter(FilterSet):
    category_id = NumberFilter(method="filter_by_category")
    title_and_content = CharFilter(method="search_by_keywords")
    title = CharFilter(method="search_by_keywords")
    content = CharFilter(method="search_by_keywords")

    class Meta:
        model = Post
        fields = ["category_id", "title", "content"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        if user is None:
            user = kwargs.pop("request").user
        self.user = user
        super().__init__(*args, **kwargs)

    @property
    def qs(self):
        queryset = super().qs

        queryset = queryset.exclude(Q(is_deleted=True) | Q(category__is_deleted=True))

        if not self.user.is_authenticated:
            queryset = queryset.exclude(Q(is_hidden=True) | Q(category__is_hidden=True))
        return queryset

    def filter_by_category(self, queryset, name, value):
        if value == 0:
            return queryset.filter(category__isnull=True)

        try:
            category = Category.objects.get(id=value)
        except Category.DoesNotExist:
            return Post.objects.none()

        if category.is_deleted:
            return Post.objects.none()

        if not self.user.is_authenticated and category.is_hidden:
            raise PermissionDeniedError("접근할 수 없는 게시판입니다")

        subcategories = category.get_descendants(include_self=True)
        return queryset.filter(category__in=subcategories)

    def search_by_keywords(self, queryset, name, value):
        fields_by_name = {
            "title_and_content": ["title", "text_content"],
            "title": ["title"],
            "content": ["text_content"],
        }

        keywords = set(value.split())
        query = Q()
        for field in fields_by_name[name]:
            for keyword in keywords:
                query |= Q(**{f"{field}__icontains": keyword})
        return queryset.filter(query)
