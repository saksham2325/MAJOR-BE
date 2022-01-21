import json

from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework import serializers

from accounts import serializers as accounts_serializers
from pokerboards import constant as pokerboard_constants, models as pokerboard_models, serializers as pokerboard_serializer


class PokerConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if not 'user' in self.scope:
            await self.close()
        self.user = self.scope['user']
        self.pokerboard_id = self.scope['url_route']['kwargs']['pokerboard_id']
        self.game_group_name = 'game_%s' % self.pokerboard_id
        print('connect')
        if pokerboard_models.Pokerboard.objects.filter(pk=self.pokerboard_id,manager=self.user).exists():
            self.game_owner_group_name = 'game_owner_%s' % self.scope['user'].pk
            print('inside.............',self.channel_layer)
            print('inside1............',self.channel_name)
            await self.channel_layer.group_add(
                self.game_owner_group_name,
                self.channel_name,
            )
        print('outside.............',self.channel_layer)
        print('outside1............',self.channel_name)
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name,
        )
        await self.accept()
        clients = getattr(self.channel_layer,
                          self.game_group_name, [])
        clients.append(self.scope["user"])
        setattr(self.channel_layer, self.game_group_name, clients)
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                pokerboard_constants.TYPE: pokerboard_constants.USER_MESSAGE,
                pokerboard_constants.MESSAGE: 'user with email {} joined the game'.format(self.user.email)
            }
        )

        await self.channel_layer.group_send(
            self.game_group_name,
            {
                pokerboard_constants.TYPE:  pokerboard_constants.ADD_USER,
                pokerboard_constants.MESSAGE: accounts_serializers.UserSerializer(clients, many=True).data,
            }
        )

    async def disconnect(self, code):
        if hasattr(self, 'game_group_name'):
            clients = getattr(self.channel_layer, self.game_group_name, [])
            clients.remove(self.scope["user"])
            setattr(self.channel_layer, self.game_group_name, clients)
            # Send message to room group
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    pokerboard_constants.TYPE: pokerboard_constants.USER_MESSAGE,
                    pokerboard_constants.MESSAGE: 'user with email {} left the game'.format(
                        self.user.email)
                }
            )
            # Send user
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    pokerboard_constants.TYPE:  pokerboard_constants.REMOVE_USER,
                    pokerboard_constants.MESSAGE: accounts_serializers.UserSerializer(clients, many=True).data,
                }
            )

            await self.channel_layer.group_discard(
                self.game_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """"
        Receieve messages sent here with type
        Messages are validated using a serializer
        """

        text_data_json = json.loads(text_data)
        serialzer = pokerboard_serializer.MessageSerializer(data=text_data_json)
        # print('....................',serialzer)
        try:
            serialzer.is_valid(raise_exception=True)
            if serialzer.data['type'] == pokerboard_constants.SUBMIT_ESTIMATE:
                """
                    To Submit an estimate of ticket
                    {
                        "type": "submit_estimate",
                        "message":{
                            "ticket": 0,
                            "estimate" : 1
                        }   
                    }
                    """
                # print(serialzer.data['message'])
                serialzer.data['message']['user'] = accounts_serializers.UserSerializer(self.user).data
                if self.game_owner_group_name:
                    print('name............',self.game_owner_group_name)
                await self.channel_layer.group_send(
                    self.game_owner_group_name,
                    {
                        pokerboard_constants.TYPE: pokerboard_constants.SUBMIT_ESTIMATE,
                        pokerboard_constants.MESSAGE: serialzer.data['message'],
                    }
                )

            elif serialzer.data['type'] == pokerboard_constants.SUBMIT_FINAL_ESTIMATE:
                serialzer.data['message']['user'] = accounts_serializers.UserSerializer(self.user).data
                await self.channel_layer.group_send(
                    self.game_group_name,
                    {
                        pokerboard_constants.TYPE: pokerboard_constants.SUBMIT_FINAL_ESTIMATE,
                        pokerboard_constants.MESSAGE: serialzer.data['message'],
                    }
                )

        except serializers.ValidationError:
            pass

    async def user_message(self, event):
        await self.send_data_to_all(event)

    async def add_user(self, event):
        "For add user in group during connection."
        await self.send_data_to_all(event)

    async def remove_user(self, event):
        "For remove user in group during disconnection."
        await self.send_data_to_all(event)

    async def submit_estimate(self, event):
        """For submitting estimates """
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'message' : event['message']
        }))

    async def submit_final_estimate(self, event):
        """For submitting final estimate by game manager """
        await self.send_data_to_all(event)

    async def send_data_to_all(self, event):
        await self.send(text_data=json.dumps({
            pokerboard_constants.TYPE: event['type'],
            pokerboard_constants.MESSAGE: event['message']
        }))

    # async def validate_estimate_message(self, event):
    #     """Validate submitted estimates"""

    #     text_data = event['message']
    #     text_data['pokerboard_id'] = self.pokerboard_id
    #     serializer = pokerboard_serializer.SubmitEstimateSerializer(data=text_data)
    #     serializer.is_valid(raise_exception=True)
    #     message = serializer.data
    #     message['user'] = accounts_serializers.UserSerializer(self.user).data
    #     return message
