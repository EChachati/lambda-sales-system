from core.models import Client, ClientIndicator
from client.serializers import ClientSerializer
from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
import json


class ClientConsumer(JsonWebsocketConsumer):

    def connect(self):
        print('ClientConsumer just connected')
        self.accept()
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        #import pdb
        # pdb.set_trace()
        self.send(json.dumps(serializer.data))
        print(json.dumps(serializer.data))

    def disconnect(self, close_code):
        pass


'''
    async def list_clients(self):
        """
        Send Json with all the clients as in the api view with the serializer data
        """
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        await self.send_json(serializer.data)
'''


def _get_clients():
    return list(Client.objects.all())


def get_clients():
    return database_sync_to_async(_get_clients, thread_sensitive=True)(10)
