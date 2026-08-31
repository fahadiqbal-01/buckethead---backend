# app/utils/cloudinary.py
import os
import cloudinary
import cloudinary.uploader

cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
api_key = os.getenv("CLOUDINARY_API_KEY")
api_secret = os.getenv("CLOUDINARY_API_SECRET")

if not cloud_name or not api_key or not api_secret:
    raise RuntimeError(
        "Cloudinary env vars are missing. Add CLOUDINARY_CLOUD_NAME, "
        "CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET to your .env file."
    )

cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret,
)


def upload_to_cloudinary(file_obj, folder="buckethead/images"):
    result = cloudinary.uploader.upload(
        file_obj,
        folder=folder,
        resource_type="image",
    )
    return result["secure_url"]