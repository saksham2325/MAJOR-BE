from rest_framework import serializers

from accounts import (serializers as account_serializers)
from pokerboards import (models as pokerboard_models,
                         constant as pokerboard_constants)


class PokerboardSerializer(serializers.ModelSerializer):

    class Meta:
        model = pokerboard_models.Pokerboard
        fields = ['id', 'name', 'manager', 'estimate_type', 'deck', 'duration']
        extra_kwargs = {'manager': {'read_only': True}}

    def create(self, validated_data):
        pokerboard = super().create(validated_data)
        pokerboard_models.UserPokerboard.objects.create(
            pokerboard=pokerboard, user=validated_data['manager'], role=[pokerboard_constants.PLAYER])
        return pokerboard


class UserPokerboardSerializer(serializers.ModelSerializer):
    user = account_serializers.UserReadSerializer(read_only=True)
    class Meta:
        model = pokerboard_models.UserPokerboard
        fields = ['id', 'user', 'role', 'pokerboard']


class MessageSerializer(serializers.Serializer):
    """Serializer for messages"""

    type = serializers.ChoiceField(choices=pokerboard_constants.TYPE_CHOICES)
    message = serializers.DictField()


class SubmitEstimateSerializer(serializers.Serializer):
    """Serializer for submitting estimates"""

    ticket = serializers.IntegerField()
    pokerboard_id = serializers.IntegerField()
    estimate = serializers.IntegerField()

    # def validate(self, data):
    #     if not pokerboard_models.Ticket.objects.filter(pk=data['ticket'], pokerboard_id=data['pokerboard_id']).exists():
    #         raise serializers.ValidationError('Ticket not exists')
    #     return data

    def to_representation(self, obj):
        # get the original representation
        data = super().to_representation(obj)
        data.pop('pokerboard_id')
        return data

    class Meta:
        model = pokerboard_models.Pokerboard
        fields = ['id', 'name']
        extra_kwargs = {'id': {'read_only': True}}
