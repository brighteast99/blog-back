from .mutation import Mutation

import graphene


schema = graphene.Schema(mutation=Mutation)
