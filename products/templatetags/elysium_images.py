"""Template tags for Cloudinary fill images."""

from django import template

register = template.Library()


def build_cloudinary_fill_url(image, width, height):
    """Build a fill-cropped Cloudinary URL."""
    if not image:
        return ""

    base_url = str(image.url) if hasattr(image, "url") else str(image)

    if "/upload/" in base_url:
        parts = base_url.split("/upload/")
        transformations = f"c_fill,g_auto,w_{width},h_{height},q_auto,f_auto"
        return f"{parts[0]}/upload/{transformations}/{parts[1]}"

    return base_url


@register.simple_tag
def cloudinary_fill(image, width, height):
    """Return a fill-cropped Cloudinary URL."""
    return build_cloudinary_fill_url(image, width, height)


@register.simple_tag
def cloudinary_fill_srcset(image, *dimensions):
    """Return a srcset string for fill-cropped sizes."""
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
