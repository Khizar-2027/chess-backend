from rest_framework import serializers
from .models import Move

class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Move
        fields = [
            "id", 
            "from_square", 
            "to_square",
            "san",
            "move_number", 
            "player", 
            "created_at"
            ]
        read_only_fields = [
            "id", 
            "player", 
            "created_at"
            ]