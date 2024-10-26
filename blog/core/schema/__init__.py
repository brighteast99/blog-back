from .category import Mutation as CategoryMuataion
from .category import Query as CategoryQuery
from .draft import Mutation as DraftMuataion
from .draft import Query as DraftQuery
from .hashtag import Query as HashtagQuery
from .post import Mutation as PostMuataion
from .post import Query as PostQuery
from .template import Mutation as TemplateMuataion
from .template import Query as TemplateQuery


class Query(CategoryQuery, HashtagQuery, PostQuery, DraftQuery, TemplateQuery):
    pass


class Mutation(CategoryMuataion, PostMuataion, DraftMuataion, TemplateMuataion):
    pass
