import os
from uuid import uuid4


def generate_upload_path(directory):
    def inner(instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        return f"{directory}/{uuid4()}{ext}"
    return inner