import graphene
from django.core.files.base import ContentFile
from django.db import DatabaseError, IntegrityError
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from blog.utils.decorators import login_required
from blog.info.models import Info


class InfoType(DjangoObjectType):
    avatar = graphene.String()

    class Meta:
        model = Info
        fields = '__all__'

    @staticmethod
    def resolve_avatar(self, info):
        return self.avatar.url if self.avatar else None


class Query(graphene.ObjectType):
    blog_info = graphene.Field(InfoType)

    @staticmethod
    def resolve_blog_info(root, info):
        return Info.objects.first()


class InfoInput(graphene.InputObjectType):
    title = graphene.String(required=False)
    description = graphene.String(required=False)
    avatar = Upload(required=False)


class UpdateInfoMutation(graphene.Mutation):
    class Arguments:
        data = InfoInput(required=True)

    success = graphene.Boolean()
    updated_info = graphene.Field(InfoType)

    @staticmethod
    @login_required
    def mutate(root, _info, **args):
        try:
            info = Info.objects.first()
        except Info.DoesNotExist:
            info = Info(title='', description='', avatar=None)

        data = args.get('data')
        info.title = data.get('title', info.title)
        info.description = data.get('description', info.description)
        if 'avatar' in data:
            avatar_image = data.get('avatar')
            if avatar_image is None:
                info.avatar.delete()
            else:
                content_file = ContentFile(avatar_image.read())
                info.avatar.save(avatar_image.name, content_file, save=True)

        try:
            info.save()
        except (DatabaseError, IntegrityError):
            return UpdateInfoMutation(success=False, updated_info=None)

        return UpdateInfoMutation(success=True, updated_info=info)


class Mutation(graphene.ObjectType):
    update_info = UpdateInfoMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
