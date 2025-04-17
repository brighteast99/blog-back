from storages.backends.s3boto3 import S3Boto3Storage


class OBS(S3Boto3Storage):
    file_overwrite = False


class OverwriteOBS(S3Boto3Storage):
    file_overwrite = True
