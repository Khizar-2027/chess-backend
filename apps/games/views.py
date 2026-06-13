from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Game
from .serializers import GameSerializer

class CreateGameView(generics.CreateAPIView):
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]


    def perform_create(self, serializer):
        serializer.save(
            white_player=self.request.user
        )

class JoinGameView(generics.UpdateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        game = self.get_object()

        if game.black_player is not None:
            return Response(
                {"error": "Game already full"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        game.black_player = request.user
        game.status = "active"
        game.save()

        serializer = self.get_serializer(game)

        return Response(serializer.data)
    
class GameListView(generics.ListAPIView):
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Game.objects.filter(status="waiting")
    
class GameDetailView(generics.RetrieveAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

class MyGamesView(generics.ListAPIView):
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Game.objects.filter(
            status="active"
        ).filter(
            white_player=user
        ) | Game.objects.filter(
            status="active",
            black_player=user
        )
    
class ResignGameView(generics.UpdateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        game = self.get_object()

        if request.user != game.white_player and request.user != game.black_player:
            return Response(
                {"error": "You are not a player in this game"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if game.status == "finished":
            return Response(
                {"error": "Game is already finished"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user == game.white_player:
            game.winner = "black"
            game.end_reason = "resignation"
        else:
            game.winner = "white"
            game.end_reason = "resignation"

        game.status = "finished"
        game.save()

        return Response({
            "status": "finished",
            "winner": game.winner,
            "end_reason": game.end_reason,
        })
    
class FinishedGamesView(generics.ListAPIView):
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Game.objects.filter(
            status="finished"
        ).filter(
            white_player=user
        ) | Game.objects.filter(
            status="finished",
            black_player=user
        ).order_by("-id")[:10]