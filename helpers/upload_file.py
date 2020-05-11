import os
import uuid
from pathlib import Path
from shutil import rmtree
from flask import current_app


def upload_image(file_storage, obj_type: str, obj_id: int):
    file_ext = os.path.splitext(file_storage.filename)[1]
    file_name = uuid.uuid4().hex + file_ext

    directory = os.path.join(current_app.config['UPLOAD_IMAGE_DIR'],
                             obj_type,
                             str(obj_id))
    Path(directory).mkdir(parents=True, exist_ok=True)
    destination = os.path.join(directory, file_name)
    file_storage.save(destination)
    url = '/'.join((current_app.config['UPLOAD_IMAGE_URL'],
                    obj_type,
                    str(obj_id),
                    file_name))
    return url


def rm_obj_images(obj_type: str, obj_id: int):
    directory = os.path.join(current_app.config['UPLOAD_IMAGE_DIR'],
                             obj_type,
                             str(obj_id))
    rmtree(directory, ignore_errors=True)
