import graphene
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import DatabaseError
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload

from blog.core.errors import InternalServerError, InvalidValueError, NotFoundError
from blog.core.schema.post import PostType
from blog.media.models import Image
from blog.media.utils import get_image
from blog.utils.decorators import login_required


class FileSizeUnit(graphene.Enum):
    B = 1
    KB = B * 1024
    MB = KB * 1024
    GB = MB * 1024


class ImageType(DjangoObjectType):
    url = graphene.String()
    name = graphene.String()
    size = graphene.Float(unit=FileSizeUnit())
    width = graphene.Int()
    height = graphene.Int()
    is_referenced = graphene.Boolean()
    thumbnail_reference_count = graphene.Int()
    post_thumbnail_of = graphene.List(PostType)
    content_reference_count = graphene.Int()
    post_content_of = graphene.List(PostType)

    class Meta:
        model = Image
        fields = "__all__"

    @staticmethod
    def resolve_url(self, info):
        return self.file.url

    def resolve_name(self, info):
        return self.file.name.split("/")[-1]

    def resolve_size(self, info, unit=FileSizeUnit.MB):
        return round(self.file.size / unit.value, 2)

    def resolve_width(self, info):
        return self.file.width

    def resolve_height(self, info):
        return self.file.height

    def resolve_is_referenced(self, info):
        return (
            self.template_thumbnail_of.exists()
            or self.draft_thumbnail_of.exists()
            or self.post_thumbnail_of.filter(is_deleted=False).exists()
            or self.template_content_of.exists()
            or self.draft_content_of.exists()
            or self.post_content_of.filter(is_deleted=False).exists()
        )

    def resolve_thumbnail_reference_count(self, info):
        count = 0
        count += self.template_thumbnail_of.count()
        count += self.draft_thumbnail_of.count()
        count += self.post_thumbnail_of.filter(is_deleted=False).count()
        return count

    def resolve_post_thumbnail_of(self, info):
        return self.post_thumbnail_of.filter(is_deleted=False).all()

    def resolve_content_reference_count(self, info):
        count = 0
        count += self.template_content_of.count()
        count += self.draft_content_of.count()
        count += self.post_content_of.filter(is_deleted=False).count()
        return count

    def resolve_post_content_of(self, info):
        return self.post_content_of.filter(is_deleted=False).all()


class Query(graphene.ObjectType):
    images = graphene.List(ImageType)
    image = graphene.Field(ImageType, id=graphene.Int(), url=graphene.String())

    @staticmethod
    def resolve_images(self, info, **kwargs):
        return Image.objects.all()

    def resolve_image(self, info, **kwargs):
        id = kwargs.get("id", None)
        url = kwargs.get("url", None)

        if id is None and url is None:
            raise InvalidValueError("id 또는 url이 필요합니다")

        if id is not None:
            try:
                return Image.objects.get(id=id)
            except Image.DoesNotExist:
                raise NotFoundError("이미지를 찾을 수 없습니다")

        if url is not None:
            image = get_image(url)
            if image is None:
                raise NotFoundError("이미지를 찾을 수 없습니다")
            return image


class UploadImageMutation(graphene.Mutation):
    class Arguments:
        file = Upload(required=True)

    url = graphene.String()

    @staticmethod
    @login_required
    def mutate(self, info, **kwargs):
        file = kwargs.get("file")
        path = default_storage.save(f"media/{file.name}"[:50], ContentFile(file.read()))
        created_image = Image.objects.create(file=path)
        return UploadImageMutation(url=created_image.file.url)


class DeleteImageMutation(graphene.Mutation):
    class Arguments:
        url = graphene.String(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, **kwargs):
        image = get_image(kwargs.get("url"))
        if image is None:
            raise NotFoundError("이미지를 찾을 수 없습니다")

        try:
            image.delete()
        except DatabaseError:
            raise InternalServerError()

        return DeleteImageMutation(success=True)


class DeleteImagesMutation(graphene.Mutation):
    class Arguments:
        urls = graphene.List(graphene.String, required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, **kwargs):
        urls = kwargs.get("urls")
        images = list(map(lambda url: get_image(url), urls))
        for image in images:
            if image is None:
                raise NotFoundError("이미지를 찾을 수 없습니다")

            try:
                image.delete()
            except DatabaseError:
                raise InternalServerError()

        return DeleteImagesMutation(success=True)


class Mutation(graphene.ObjectType):
    upload_image = UploadImageMutation.Field()
    delete_image = DeleteImageMutation.Field()
    delete_images = DeleteImagesMutation.Field()
