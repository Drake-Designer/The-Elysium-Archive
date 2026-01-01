"""
Custom template tags for Cloudinary fill-based images.

Strategy: Always use c_fill with g_auto to fill containers completely.
Cropping is acceptable, letterboxing is not.

Usage in templates:
    {% load elysium_images %}
    {% cloudinary_fill product.image 400 225 %}
"""

from django import template

register = template.Library()


def build_cloudinary_fill_url(image, width, height):
    """
    Build a Cloudinary URL with fill-based cropping.

    Uses c_fill with g_auto for intelligent automatic cropping.
    Always includes q_auto and f_auto for optimization.
    """
    if not image:
        return ""

    # Get the base URL from CloudinaryField
    base_url = str(image.url) if hasattr(image, "url") else str(image)

    # Cloudinary URL structure: .../upload/transformations/public_id.ext
    if "/upload/" in base_url:
        parts = base_url.split("/upload/")
        transformations = f"c_fill,g_auto,w_{width},h_{height},q_auto,f_auto"
        return f"{parts[0]}/upload/{transformations}/{parts[1]}"

    return base_url


@register.simple_tag
def cloudinary_fill(image, width, height):
    """
    Generate a Cloudinary URL with fill cropping.

    Args:
        image: CloudinaryField instance
        width: Target width in pixels
        height: Target height in pixels

    Returns:
        Transformed Cloudinary URL string

    Example:
        {% cloudinary_fill product.image 400 225 %}
    """
    return build_cloudinary_fill_url(image, width, height)


@register.simple_tag
def cloudinary_fill_srcset(image, *dimensions):
    """
    Generate srcset with multiple fill-cropped sizes.

    Args:
        image: CloudinaryField instance
        *dimensions: Pairs of width,height values

    Returns:
        srcset string like "url1 300w, url2 400w, url3 600w"

    Example:
        {% cloudinary_fill_srcset product.image 300 169 400 225 600 338 %}
    """
    if not image:
        return ""

    dims = list(dimensions)
    if len(dims) % 2 != 0:
        return ""

    srcset_parts = []
    for i in range(0, len(dims), 2):
        width = dims[i]
        height = dims[i + 1]
        url = build_cloudinary_fill_url(image, width, height)
        srcset_parts.append(f"{url} {width}w")

    return ", ".join(srcset_parts)
