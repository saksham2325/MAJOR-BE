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
