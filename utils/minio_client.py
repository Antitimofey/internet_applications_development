
import os
from minio import Minio
from django.conf import settings

def get_minio_client():
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_USE_SSL
    )

def ensure_bucket_exists(bucket_name):
    client = get_minio_client()
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)