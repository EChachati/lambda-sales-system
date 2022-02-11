import requests


class Test:
    token = '7cb314eada11bc3995f57c6d8dd42e795a4d2f2d'
    deploy = "https://lambda-sales-api.azurewebsites.net/api/client/"
    localhost = "http://127.0.0.1:8000/api/client/"
    headers = {
        'Authorization': 'Token ' + token
    }

    def test_get_client(self):
        res = requests.get(
            self.deploy, headers=self.headers)
        #assert res.status_code == 200
        return res.json()


if __name__ == "__main__":
    test = Test()
    print(test.test_get_client())
    #import os
    # print(os.getenv('DB_PASSWORD'))
