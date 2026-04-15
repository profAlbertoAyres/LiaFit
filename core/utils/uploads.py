import os
import uuid


IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'webp', 'bmp', 'gif', 'tif', 'tiff')
VIDEO_EXTENSIONS = ('mp4', 'mov', 'avi', 'mkv')


def smart_upload_to(instance, filename):

    app_label = instance._meta.app_label
    model_name = instance._meta.model_name

    ext = filename.split('.')[-1].lower()

    if ext in IMAGE_EXTENSIONS:
        folder = 'img'
    elif ext in VIDEO_EXTENSIONS:
        folder = 'video'
    else:
        folder = 'files'

    new_filename = f"{uuid.uuid4().hex}.{ext}"

    pk = instance.pk

    if pk is None:
        pk = "temp"

    return os.path.join(
        app_label,
        model_name,
        folder,
        str(pk),
        new_filename
    )