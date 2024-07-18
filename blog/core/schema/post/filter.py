from django.db.models import Q
from django_filters import FilterSet, CharFilter, NumberFilter

from blog.core.errors import PermissionDeniedError
from blog.core.models import Category, Post


class PostFilter(FilterSet):
    category_id = NumberFilter(method='filter_by_category')
    title = CharFilter(method='search_by_keywords')
    content = CharFilter(method='search_by_keywords')

    class Meta:
        model = Post
        fields = ['category_id', 'title', 'content']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        self.user = request.user
        super().__init__(*args, **kwargs)

    @property
    def qs(self):
        queryset = super().qs

        queryset = queryset.exclude(Q(is_deleted=True) |
                                    Q(category__is_deleted=True))

        if not self.user.is_authenticated:
            queryset = queryset.exclude(Q(is_hidden=True) |
                                        Q(category__is_hidden=True))
        return queryset

    def filter_by_category(self, queryset, name, value):
        if value == 0:
            return queryset.filter(category__isnull=True)

        try:
            category = Category.objects.get(id=value)
        except Category.DoesNotExist:
            return Category.objects.none()

        if category.is_deleted:
            return Category.objects.none()

        if not self.user.is_authenticated and category.is_hidden:
            raise PermissionDeniedError()

        subcategories = category.get_descendants(include_self=True)
        return queryset.filter(category__in=subcategories)

    def search_by_keywords(self, queryset, name, value):
        field_by_name = {"title": "title", "content": "text_content"}

        keywords = value.split()
        query = Q()
        for keyword in keywords:
            query |= Q(**{f"{field_by_name[name]}__icontains": keyword})
        return queryset.filter(query)
