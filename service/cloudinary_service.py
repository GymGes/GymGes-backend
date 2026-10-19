import cloudinary.uploader

from core import cloudinary_config


def upload_image(image, folder: str):
    return cloudinary.uploader.upload(
        image,
        folder=folder
    )


def delete_image(public_id: str):
    return cloudinary.uploader.destroy(public_id)
