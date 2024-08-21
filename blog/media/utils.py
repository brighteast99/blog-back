from urllib.parse import unquote

from blog.media.models import Image
from blog.settings import AWS_S3_CUSTOM_DOMAIN


def get_filename_from_url(url):
    return unquote(url.split(AWS_S3_CUSTOM_DOMAIN)[-1][1:])


def get_image(url=None):
    if url is None:
        return None

    return Image.objects.get(file__endswith=get_filename_from_url(url))


def get_images(urls=None):
    if urls is None or len(urls) == 0:
        return []
    return map(
        lambda url: Image.objects.get(file__endswith=get_filename_from_url(url)), urls
    )
