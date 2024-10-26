from django_filters import CharFilter, FilterSet

from blog.core.models import Hashtag


class HashtagFilter(FilterSet):
    keyword = CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Hashtag
        fields = ["name"]
