from os.path import splitext

import graphene
from django.core.files.base import ContentFile
from django.db import DatabaseError, IntegrityError
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload

from blog.core.errors import InternalServerError
from blog.info.models import Info
from blog.utils.decorators import login_required


class InfoType(DjangoObjectType):
    avatar = graphene.String()
    favicon = graphene.String()

    class Meta:
        model = Info
        fields = "__all__"

    @staticmethod
    def resolve_avatar(self, info):
        return self.avatar.url if self.avatar else None

    @staticmethod
    def resolve_favicon(self, info):
        return self.favicon.url if self.favicon else None


class Query(graphene.ObjectType):
    blog_info = graphene.Field(InfoType)

    @staticmethod
    def resolve_blog_info(self, info):
        return Info.objects.first()


class InfoInput(graphene.InputObjectType):
    title = graphene.String(required=False)
    description = graphene.String(required=False)
    avatar = Upload(required=False)
    favicon = Upload(required=False)


class UpdateInfoMutation(graphene.Mutation):
    class Arguments:
        data = InfoInput(required=True)

    success = graphene.Boolean()
    updated_info = graphene.Field(InfoType)

    @staticmethod
    @login_required
    def mutate(self, _info, **kwargs):
        try:
            info = Info.objects.first()
        except Info.DoesNotExist:
            info = Info(title="", description="", avatar=None)

        data = kwargs.get("data")
        info.title = data.get("title", info.title)
        info.description = data.get("description", info.description)
        if "avatar" in data:
            avatar_image = data.get("avatar")
            info.avatar.delete()
            if avatar_image is not None:
                content_file = ContentFile(avatar_image.read())
                _, ext = splitext(avatar_image.name)
                info.avatar.save(f"profile{ext}", content_file, save=True)
        if "favicon" in data:
            favicon = data.get("favicon")
            if favicon is None:
                info.favicon.delete()
            else:
                content_file = ContentFile(favicon.read())
                info.favicon.save("favicon.ico", content_file, save=True)

        try:
            info.save()
        except (DatabaseError, IntegrityError):
            raise InternalServerError()

        return UpdateInfoMutation(success=True, updated_info=info)


class Mutation(graphene.ObjectType):
    update_info = UpdateInfoMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
