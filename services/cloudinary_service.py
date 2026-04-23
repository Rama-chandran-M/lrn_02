import cloudinary
import cloudinary.uploader
import io
from config.settings import CLOUDINARY_CONFIG

cloudinary.config(**CLOUDINARY_CONFIG)

def upload_file(file):
    file_bytes = file.read()
    file.seek(0)

    result = cloudinary.uploader.upload(
        io.BytesIO(file_bytes),
        resource_type="raw",
        access_mode="public"
    )

    return result.get("secure_url")