"""Template tags for Cloudinary fill images."""


from django import template
import logging


register = template.Library()
logger = logging.getLogger(__name__)


def build_cloudinary_fill_url(image, width, height):
    """Build a fill-cropped Cloudinary URL with error handling."""
    if not image:
        logger.debug("cloudinary_fill: image is None or empty")
        return ""

    try:
        # Get URL from CloudinaryField
        base_url = str(image.url) if hasattr(image, "url") else str(image)

        if not base_url:
            logger.warning(f"cloudinary_fill: Empty URL for image {image}")
            return ""

        # Force HTTPS for mixed content prevention
        if base_url.startswith("http://"):
            base_url = base_url.replace("http://", "https://", 1)
            logger.debug(f"cloudinary_fill: Converted HTTP to HTTPS")

        # Check if it's a Cloudinary URL
        if "/upload/" not in base_url:
            logger.warning(
                f"cloudinary_fill: URL missing /upload/: {base_url[:100]}"
            )
            # Return original URL as fallback
            return base_url

        # Build transformed URL
        parts = base_url.split("/upload/")
        transformations = f"c_fill,g_auto,w_{width},h_{height},q_auto,f_auto"
        transformed_url = f"{parts[0]}/upload/{transformations}/{parts[1]}"

        logger.debug(f"cloudinary_fill: Generated {transformed_url[:100]}")
        return transformed_url

    except Exception as e:
        logger.error(f"cloudinary_fill error: {e}", exc_info=True)
        # Return empty string to trigger {% else %} block in template
        return ""


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
        logger.warning(
            f"cloudinary_fill_srcset: Odd number of dimensions: {dims}"
        )
        return ""

    srcset_parts = []
    for i in range(0, len(dims), 2):
        width = dims[i]
        height = dims[i + 1]
        url = build_cloudinary_fill_url(image, width, height)
        if url:  # Only add if URL generated successfully
            srcset_parts.append(f"{url} {width}w")

    result = ", ".join(srcset_parts)
    logger.debug(f"cloudinary_fill_srcset: Generated {len(srcset_parts)} URLs")
    return result


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key in templates."""
    if dictionary is None:
        return None
    return dictionary.get(key)
