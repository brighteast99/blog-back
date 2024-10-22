from ast import literal_eval

from django.db.models import Q
from django_filters import CharFilter, FilterSet, NumberFilter

from blog.core.errors import PermissionDeniedError
from blog.core.models import Category, Post


class PostFilter(FilterSet):
    category_id = NumberFilter(method="filter_by_category")
    title_and_content = CharFilter(method="search_by_keywords")
    title = CharFilter(method="search_by_keywords")
    content = CharFilter(method="search_by_keywords")
    tag = CharFilter(method="search_by_tags")

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

        queryset = queryset.exclude(is_deleted=True)

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

    def search_by_tags(self, queryset, name, value):
        value = literal_eval(value)
        if len(value):
            return queryset.filter(tags__name__in=value).distinct()
        else:
            return queryset

    @staticmethod
    def find_matching_intervals(str, keywords):
        if len(keywords) <= 0:
            return []

        intervals = []
        for keyword in keywords:
            cur = 0
            while cur < len(str):
                cur = str.find(keyword, cur)
                if cur == -1:
                    break
                intervals.append([cur, cur + len(keyword)])
                cur += len(keyword)

        if len(intervals) < 2:
            return intervals

        intervals.sort(key=lambda x: x[0])
        merged_intervals = [intervals[0]]

        for [start, end] in intervals[1:]:
            prev_start, prev_end = merged_intervals[-1]
            if start <= prev_end or not str[prev_end:start].strip():
                merged_intervals[-1] = [prev_start, max(prev_end, end)]
            else:
                merged_intervals.append([start, end])

        return merged_intervals

    @staticmethod
    def longest_matched_text(post):
        match_length = lambda highlight: highlight[1] - highlight[0]
        longest_match_title = max(map(match_length, [*post.title_highlights, [0, 1]]))
        longest_match_content = max(
            map(match_length, [*post.content_highlights, [0, 1]])
        )
        longest_match = max(longest_match_title, longest_match_content)
        return (
            longest_match,
            longest_match_title,
            longest_match_content,
            len(post.title_highlights) + len(post.content_highlights),
        )

    @staticmethod
    def matched_tags(tag):
        def _matched_tags(post):
            return post.tags.filter(name__in=tag).count()

        return _matched_tags
