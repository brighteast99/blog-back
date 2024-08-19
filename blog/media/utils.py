from urllib.parse import unquote

from blog.media.models import Image

def get_filename_from_url(url):
    return unquote(url.split("/")[-1])


def get_image(url=None):
    if url is None:
        return None

    return Image.objects.get(file__endswith=get_filename_from_url(url))


def get_images(urls=None):
    if urls is None or len(urls) == 0:
        return map(lambda image: image.file.url, Image.objects.all())
    return map(
        lambda url: Image.objects.get(file__endswith=get_filename_from_url(url)), urls
    )
