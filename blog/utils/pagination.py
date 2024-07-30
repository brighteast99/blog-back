import graphene


class PageInfoType(graphene.ObjectType):
    pages = graphene.Int()
    current_page = graphene.Int()
