from storages.backends.s3boto3 import S3Boto3Storage


class Cafe24OBS(S3Boto3Storage):
    file_overwrite = False
