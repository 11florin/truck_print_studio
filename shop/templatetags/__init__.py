*** Add File: /home/florin/projects/truck_print_studio/shop/templatetags/image_tags.py
from django import template
from django.utils.http import urlencode


register = template.Library()


@register.filter
def cloudinary_image(url, width):
    if not url or "/image/upload/" not in url:
        return url

    params = urlencode({
        "f": "auto",
        "q": "auto",
        "w": str(width),
        "c": "limit",
    }).replace("&", ",")
    params = params.replace("%2C", ",")
    params = params.replace("f=f_auto", "f_auto")
    params = params.replace("q=auto", "q_auto")
    params = params.replace("w=", "w_").replace("c=", "c_")

    return url.replace("/image/upload/", f"/image/upload/{params}/", 1)
