from graphene import Node
from base64 import b64decode
from blog.core.errors import InvalidValueError


def localid(global_id):
    try:
        decoded = b64decode(global_id).decode('UTF-8').split(':')
        if len(decoded) < 2:
            raise InvalidValueError('Invalid global id')
    except:
        return None

    _, local_id = decoded
    return local_id


def globalid(type, local_id):
    return Node.to_global_id(type, local_id)
