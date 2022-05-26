import pdb
import requests
import json
import base64
from typing import List
import pickle
from sklearn.impute import SimpleImputer
import pandas as pd
from datetime import datetime
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

    date_start = request.query_params.get('date_start', None)
    date_end = request.query_params.get('date_end', None)
    date_format = '%Y-%m-%d'
    q = q.filter(date__gte=datetime.strptime(
        date_start, date_format)) if date_start else q
    q = q.filter(date__lte=datetime.strptime(
        date_end, date_format)) if date_end else q

    for f in possible_filters:
        param = request.query_params.get(f) if f else None
        if param:
            q = q.filter(**{f: param})
    return q


def save_model(model, name):
    """
    It takes a model and a name, and saves the model as a pickle file with the name you gave it

    :param model: The model you want to save
    :param name: The name of the model
    """
    with open(f"core/models_ia/{name}.pkl", "wb") as f:
        pickle.dump(model, f)


def load_model(name):
    """
    It loads a model from a file

    :param name: The name of the model
    :return: The model is being returned. None if it doesn't exist
    """
    try:
        with open(f"core/models_ia/{name}.pkl", "rb") as f:
            model = pickle.load(f)
        return model
    except:
        return None


def predict(model, income: List, count: List, month=None):
    """
    It takes in a model, a list of incomes, and a list of counts, and returns a list of predictions

    :param model: The model you want to use to predict the data
    :param income: List of income values
    :type income: List
    :param count: The number of people in the household
    :type count: List
    :return: The predicted values for the given data.
    """
    data = SimpleImputer().fit_transform(
        pd.DataFrame({'income': income, 'count': count})
    )
    if month:
        data = SimpleImputer().fit_transform(
            pd.DataFrame({'income': income, 'count': count, "month": month})
        )
    return model.predict(data)
