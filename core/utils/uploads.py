"""
Define onde os arquivos enviados (fotos, vídeos, documentos) são salvos.
Usado como `upload_to=smart_upload_to` em ImageField/FileField.
"""
import os
import uuid

from django.core.exceptions import ValidationError


# Extensões aceitas como imagem.
IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'webp', 'bmp', 'gif', 'tif', 'tiff')

# Extensões aceitas como vídeo.
VIDEO_EXTENSIONS = ('mp4', 'mov', 'avi', 'mkv', 'webm')

# Extensões PROIBIDAS por segurança (executáveis e scripts).
BLOCKED_EXTENSIONS = (
    'exe', 'sh', 'bat', 'cmd', 'com', 'msi',
    'php', 'asp', 'aspx', 'jsp',
    'js', 'html', 'htm', 'svg',
    'dll', 'so',
)


def smart_upload_to(instance, filename: str) -> str:
    """
    Monta o caminho onde o arquivo será salvo.

    Estrutura final:
        {app}/{model}/{tipo}/{pk}/{uuid}.{ext}

    Exemplo:
        account/user/img/42/a1b2c3d4....jpg
    """
    app_label = instance._meta.app_label
    model_name = instance._meta.model_name

    # 1) Pega a extensão de forma segura (lida com arquivos sem extensão).
    parts = filename.rsplit('.', 1)
    ext = parts[1].lower() if len(parts) == 2 else ''

    # 2) Bloqueia extensões perigosas.
    if ext in BLOCKED_EXTENSIONS:
        raise ValidationError(f'Tipo de arquivo não permitido: .{ext}')

    # 3) Define a pasta pelo tipo do arquivo.
    if ext in IMAGE_EXTENSIONS:
        folder = 'img'
    elif ext in VIDEO_EXTENSIONS:
        folder = 'video'
    else:
        folder = 'files'

    # 4) Gera nome único (UUID sem hífens) preservando a extensão.
    new_filename = f'{uuid.uuid4().hex}.{ext}' if ext else uuid.uuid4().hex

    # 5) Se o objeto ainda não foi salvo, usa 'temp' como pasta.
    pk = instance.pk if instance.pk is not None else 'temp'

    return os.path.join(app_label, model_name, folder, str(pk), new_filename)
