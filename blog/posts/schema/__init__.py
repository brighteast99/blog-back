from .category import Query as CategoryQuery, Mutation as CategoryMuataion
from .post import Query as PostQuery, Mutation as PostMuataion
from .draft import Query as DraftQuery, Mutation as DraftMuataion
from .template import Query as TemplateQuery, Mutation as TemplateMuataion
from .common import Mutation as CommonMutation


class Query(
    CategoryQuery,
    PostQuery,
    DraftQuery,
    TemplateQuery
):
    pass


class Mutation(
    CategoryMuataion,
    PostMuataion,
    DraftMuataion,
    TemplateMuataion,
    CommonMutation
):
    pass
