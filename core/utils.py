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
