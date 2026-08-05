import os
from uuid import uuid4


def generate_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"salons/{uuid4()}{ext}"
