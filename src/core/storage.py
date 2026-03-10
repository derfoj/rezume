import os
import cloudinary
import cloudinary.uploader
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Configure Cloudinary
# Expected env: CLOUDINARY_URL or individual keys
if os.getenv("CLOUDINARY_URL"):
    cloudinary.config(secure=True)
else:
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )

def upload_file_to_cloud(file_path: str, folder: str = "rezume"):
    """
    Uploads a local file to Cloudinary and returns the secure URL.
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found for upload: {file_path}")
            return None

        response = cloudinary.uploader.upload(
            file_path,
            folder=f"rezume/{folder}",
            resource_type="auto" # Handles PDF, JPG, PNG, etc.
        )
        return response.get("secure_url")
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        return None

def delete_file_from_cloud(public_id: str):
    """Deletes a file from Cloudinary."""
    try:
        cloudinary.uploader.destroy(public_id)
        return True
    except Exception as e:
        logger.error(f"Cloudinary deletion failed: {e}")
        return False
