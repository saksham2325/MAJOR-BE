from rest_framework import generics, viewsets
from rest_framework.response import Response

from pokerboards import (constant as poker_constants, models as pokerboard_models, serializers as pokerboard_serializers)


class PokerboardViewsets(viewsets.ModelViewSet):
    serializer_class = pokerboard_serializers.PokerboardSerializer
    
    def  get_queryset(self):
        return pokerboard_models.Pokerboard.objects.filter(manager=self.request.user)
        
    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)


class UserPokerboardView(generics.ListAPIView, generics.DestroyAPIView):
    serializer_class = pokerboard_serializers.UserPokerboardSerializer
    
    def get_queryset(self):
        queryset = pokerboard_models.UserPokerboard.objects.all()
        pokerboard_id = self.request.query_params.get('pokerboard_id')
        if pokerboard_id:
            queryset = queryset.filter(pokerboard_id=pokerboard_id)
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        user_pokerboard_obj = self.get_object()
        user_pokerboard_obj.delete()
        return Response({'message': poker_constants.USER_REMOVED})
