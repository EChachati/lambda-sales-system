import requests
import json
import base64

API_KEY = '77643199c4393578689646652b98080a'


def upload_image(image) -> str:

    contents = image.read()
    data = base64.b64encode(contents)
    url = f"https://api.imgbb.com/1/upload?key={API_KEY}"

    response = requests.post(
        url,
        data={'image': data}
    )

    image_url = json.loads(response.text)['data']['image']['url']

    return image_url


def apply_query_filters(request, queryset):
    """
    It takes a Django request object and a Django queryset, and returns a new queryset that is filtered
    by the query parameters in the request

    :param request: The request object
    :param queryset: The queryset you want to filter
    :return: Filtered queryset.
    """
    q = queryset
    possible_filters = queryset.first().to_dict().keys()
    for f in possible_filters:
        param = request.query_params.get(f) if f else None
        if param:
            q = q.filter(**{f: param})
    return q
