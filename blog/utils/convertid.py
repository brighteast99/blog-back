from graphene import Node
from base64 import b64decode


def localid(global_id):
    _, local_id = b64decode(global_id).decode('UTF-8').split(':')
    return local_id


def globalid(type, local_id):
    return Node.to_global_id(type, local_id)
