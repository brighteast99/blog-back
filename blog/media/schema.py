import graphene
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import DatabaseError
from graphene_file_upload.scalars import Upload

from blog.core.errors import InternalServerError, NotFoundError
from blog.media.models import Image
from blog.media.utils import get_images
from blog.utils.decorators import login_required


class Query(graphene.ObjectType):
    images = graphene.List(graphene.String)

    @staticmethod
    def resolve_images(self, info, **kwargs):
        return get_images()


class UploadImageMutation(graphene.Mutation):
    class Arguments:
        file = Upload(required=True)

    url = graphene.String()

    @staticmethod
    @login_required
    def mutate(self, info, **kwargs):
        file = kwargs.get("file")
        path = default_storage.save(f"media/{file.name}", ContentFile(file.read()))
        created_image = Image.objects.create(file=path)
        return UploadImageMutation(url=created_image.file.url)


class DeleteImageMutation(graphene.Mutation):
    class Arguments:
        url = graphene.String(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, **kwargs):
        try:
            image = Image.objects.get(file=kwargs.get("url"))
            image.delete()
            return DeleteImageMutation(success=True)
        except Image.DoesNotExist:
            raise NotFoundError("이미지를 찾을 수 없습니다")
        except DatabaseError:
            raise InternalServerError()


class Mutation(graphene.ObjectType):
    upload_image = UploadImageMutation.Field()
    delete_image = DeleteImageMutation.Field()
