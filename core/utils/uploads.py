import os
import uuid
from datetime import datetime
from pathlib import Path

from django.core.exceptions import ValidationError


FILE_CATEGORIES = {
    'img':   {'jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'tif', 'tiff'},
    'video': {'mp4', 'mov', 'avi', 'mkv', 'webm'},
    'audio': {'mp3', 'wav', 'ogg', 'm4a', 'aac'},
    'doc':   {'pdf', 'docx', 'xlsx', 'txt', 'csv'},
}

BLOCKED_EXTENSIONS = {
    'exe', 'sh', 'bat', 'cmd', 'com', 'msi',
    'php', 'js', 'html', 'htm', 'svg',
    'dll', 'so', 'py', 'rb', 'jar',
}

FALLBACK_CATEGORY = 'files'

def get_file_category(extension: str) -> str:
    ext = extension.lower().lstrip('.')
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return FALLBACK_CATEGORY

def is_extension_blocked(extension: str) -> bool:
    ext = extension.lower().lstrip('.')
    return ext in BLOCKED_EXTENSIONS

def smart_upload_to(instance, filename: str) -> str:
    ext = Path(filename).suffix.lower().lstrip('.')

    if is_extension_blocked(ext):
        raise ValueError(f"Extensão '.{ext}' não permitida por segurança")

    category = get_file_category(ext)

    app_label = instance._meta.app_label
    model_name = instance._meta.model_name
    pk = instance.pk or 'temp'
    year = datetime.now().year

    unique_name = f"{uuid.uuid4().hex}.{ext}"
    
    return f"{app_label}/{model_name}/{category}/{pk}/{year}/{unique_name}"

