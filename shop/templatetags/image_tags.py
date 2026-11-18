from django import template


register = template.Library()


@register.filter
def cloudinary_image(url, width):
    if not url or "/image/upload/" not in url:
        return url

    params = f"f_auto,q_auto,w_{width},c_limit"
    return url.replace("/image/upload/", f"/image/upload/{params}/", 1)
