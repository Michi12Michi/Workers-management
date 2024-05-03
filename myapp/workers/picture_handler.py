import os
from flask import url_for, current_app
from PIL import Image

def add_profile_pic(pic_upload, username):
    filename = pic_upload.filename
    ext = filename.split(".")[-1]
    storage_filename = str(username) + "." + ext
    filepath = os.path.join(current_app.root_path, "static/profile_pics", storage_filename)
    # DEFINIZIONE DELLA MISURA, EVENTUALMENTE MODIFICABILE
    output_size = (200, 200)
    pic = Image.open(pic_upload)
    pic.thumbnail(output_size)
    pic.save(filepath)
    return storage_filename
