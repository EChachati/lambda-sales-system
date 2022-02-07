import requests


class Test:
    token = 'e3cb0e121a9c4739fafb6a34bb2309b988fa60cc'
    headers = {
        'Authorization': 'Token ' + token
    }

    def test_get_client(self):
        res = requests.get(
            "http://127.0.0.1:8000/api/client/", headers=self.headers)
        assert res.status_code == 200
        return res.json()


if __name__ == "__main__":
    test = Test()
    print(test.test_get_client())
