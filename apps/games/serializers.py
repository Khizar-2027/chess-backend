from rest_framework import serializers
from .models import Game

class GameSerializer(serializers.ModelSerializer):

    white_player_username = serializers.CharField(
        source="white_player.username",
        read_only=True
    )

    black_player_username = serializers.CharField(
        source="black_player.username",
        read_only=True
    )
    
    class Meta:
        model = Game
        fields = [
            "id",
            "white_player",
            "black_player",
            "white_player_username",
            "black_player_username",
            "status",
            "current_turn",
            "board_state",
            "white_time",
            "black_time",
            "winner",
            "end_reason",
        ]
        read_only_fields = [
            "white_player",
            "black_player",
            "white_player_username",
            "black_player_username",
            "status",
            "current_turn",
            "board_state"
        ]