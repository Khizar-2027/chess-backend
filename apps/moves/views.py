from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import chess
from .models import Move
from .serializers import MoveSerializer
from apps.games.models import Game

from django.utils import timezone
from datetime import timedelta

class CreateMoveView(generics.CreateAPIView):
    serializer_class = MoveSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        game_id = self.kwargs.get("game_id")

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"error": "Game not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if game.status != "active":
            return Response(
                {"error": "Game is not active"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if game.current_turn == "white" and request.user != game.white_player:
            return Response(
                {"error": "It's white player's turn"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if game.current_turn == "black" and request.user != game.black_player:
            return Response(
                {"error": "It's black player's turn"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        move_text = request.data.get("move")
        if not move_text:
            return Response(
                {"error": "Move is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        promotion = request.data.get("promotion")
        if promotion:
            allowed = ["q", "r", "b", "n"]
            if promotion not in allowed:
                return Response(
                    {"error": "Invalid promotion piece. Use q, r, b or n"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            move_text = move_text + promotion

        now = timezone.now()

        time_diff = (now - game.last_move_time).total_seconds()

        board = chess.Board(game.board_state)

        try:
            chess_move = chess.Move.from_uci(move_text)
        except ValueError:
            return Response(
                {"error": "Invalid move format. Use UCI format like e2e4"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if chess_move not in board.legal_moves:
            return Response(
                {"error": "Illegal move"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        san_move = board.san(chess_move)
        board.push(chess_move)

        if game.current_turn == "white":
            game.white_time -= int(time_diff)
        else:
            game.black_time -= int(time_diff)

        game.board_state = board.fen()

        game.current_turn = (
            "black"
            if game.current_turn == "white"
            else "white"
            )

        if board.is_checkmate():
            game.status = "finished"

        if game.white_time <= 0 or game.black_time <= 0:
            game.status = "finished"

        game.save()

        Move.objects.create(
            game=game,
            player=request.user,
            from_square=move_text[:2],
            to_square=move_text[2:4],
            san=san_move,
            move_number=Move.objects.filter(game=game).count() + 1,
        )

        return Response(
            {
                "move": f"{move_text[:2]} -> {move_text[2:4]}",
                "board_state": game.board_state,
                "white_time": game.white_time,
                "black_time": game.black_time,
                "current_turn": game.current_turn,
                "status": game.status,
                "is_check": board.is_check(),
                "is_checkmate": board.is_checkmate(),
            },
            status=status.HTTP_201_CREATED,
        )
    
class ListMovesView(generics.ListAPIView):
    serializer_class=MoveSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        game_id = self.kwargs.get("game_id")

        return Move.objects.filter(
            game_id=game_id
        ).order_by("move_number")