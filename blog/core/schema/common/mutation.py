import uuid
import graphene
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from graphene_file_upload.scalars import Upload
from blog.utils.decorators import login_required
from urllib.parse import urlparse


class UploadImageMutation(graphene.Mutation):
    class Arguments:
        file = Upload(required=True)

    url = graphene.String()

    @staticmethod
    @login_required
    def mutate(self, info, **args):
        file = args.get('file')
        name, ext = file.name.rsplit('.', 1)
        path = default_storage.save(
            f'media/{name}_{uuid.uuid4()}.{ext}', ContentFile(file.read()))
        return UploadImageMutation(url=default_storage.url(path))


class DeleteImageMutation(graphene.Mutation):
    class Arguments:
        url = graphene.String(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, **args):
        file_path = '/'.join(urlparse(args.get('url')).path.split('/', 2)[2:])

        if default_storage.exists(file_path):
            default_storage.delete(file_path)
            return DeleteImageMutation(success=True)
        return DeleteImageMutation(success=False)


class Mutation(graphene.ObjectType):
    upload_image = UploadImageMutation.Field()
    delete_image = DeleteImageMutation.Field()
