import graphene

from .mutation import Mutation

schema = graphene.Schema(mutation=Mutation)
