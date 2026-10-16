from urllib.parse import urlparse

import cloudinary

from core.config import CLOUDINARY_URL

if CLOUDINARY_URL:
    parsed = urlparse(CLOUDINARY_URL)
    cloudinary.config(
        cloud_name=parsed.hostname,
        api_key=parsed.username,
        api_secret=parsed.password,
    )
