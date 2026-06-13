import json
import chess
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Game
from apps.moves.models import Move


class GameConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.room_group_name = f"game_{self.game_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        game = await self.get_game()
        if game:
            moves = await self.get_moves()
            await self.send(text_data=json.dumps({
                "type": "game_state",
                "board_state": game.board_state,
                "current_turn": game.current_turn,
                "white_time": game.white_time,
                "black_time": game.black_time,
                "status": game.status,
                "white_player_username": game.white_player.username,
                "black_player_username": game.black_player.username if game.black_player else None,
                "moves": moves,
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "move":
            await self.handle_move(data)
        
        elif message_type == "resign":
            await self.handle_resign()

    async def handle_move(self, data):
        game = await self.get_game()
        user = self.scope["user"]
        move_text = data.get("move")
        promotion = data.get("promotion")

        if not game or game.status != "active":
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Game is not active"
            }))
            return

        if game.current_turn == "white" and user != game.white_player:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "It's white player's turn"
            }))
            return

        if game.current_turn == "black" and user != game.black_player:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "It's black player's turn"
            }))
            return

        if promotion:
            allowed = ["q", "r", "b", "n"]
            if promotion not in allowed:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Invalid promotion piece"
                }))
                return
            move_text = move_text + promotion

        now = timezone.now()
        time_diff = (now - game.last_move_time).total_seconds()
        board = chess.Board(game.board_state)

        try:
            chess_move = chess.Move.from_uci(move_text)
        except ValueError:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Invalid move format. Use UCI like e2e4"
            }))
            return

        if chess_move not in board.legal_moves:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Illegal move"
            }))
            return

        san_move = board.san(chess_move)
        board.push(chess_move)

        if game.current_turn == "white":
            game.white_time -= int(time_diff)
        else:
            game.black_time -= int(time_diff)

        game.board_state = board.fen()
        game.current_turn = "black" if game.current_turn == "white" else "white"

        is_checkmate = board.is_checkmate()
        is_check = board.is_check()
        is_stalemate = board.is_stalemate()
        is_draw = (
            board.is_insufficient_material() or
            board.is_seventyfive_moves() or
            board.is_fivefold_repetition() or
            is_stalemate
        )

        if is_checkmate:
            game.status = "finished"
            game.winner = "black" if game.current_turn == "white" else "white"
            game.end_reason = "checkmate"
        elif is_draw:
            game.status = "finished"
            game.winner = None
            game.end_reason = "stalemate" if is_stalemate else "draw"
        elif game.white_time <= 0 or game.black_time <= 0:
            game.status = "finished"
            game.winner = "black" if game.white_time <= 0 else "white"
            game.end_reason = "timeout"

        await self.save_game(game)
        move_count = await self.get_move_count()
        await self.save_move(
            game=game,
            player=user,
            from_square=move_text[:2],
            to_square=move_text[2:4],
            san=san_move,
            move_number=move_count + 1,
        )

        moves = await self.get_moves()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_update",  
                "board_state": game.board_state,
                "current_turn": game.current_turn,
                "white_time": game.white_time,
                "black_time": game.black_time,
                "status": game.status,
                "is_check": is_check,
                "is_checkmate": is_checkmate,
                "is_stalemate": is_stalemate,
                "is_draw": is_draw,   
                "winner": game.winner,
                "end_reason": game.end_reason,
                "moves": moves,
                "last_move": {
                    "from": move_text[:2],
                    "to": move_text[2:4],
                }
            }
        )
    
    async def handle_resign(self):
        game = await self.get_game()
        user = self.scope["user"]

        if not game or game.status != "active":
            return
        
        if user != game.white_player and user != game.black_player:
            return
        
        if user == game.white_player:
            game.winner = "black"
        else:
            game.winner = "white"

        game.end_reason = "resignation"
        game.status = "finished"
        await self.save_game(game)

        moves = await self.get_moves()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_update",
                "board_state": game.board_state,
                "current_turn": game.current_turn,
                "white_time": game.white_time,
                "black_time": game.black_time,
                "status": game.status,
                "is_check": False,
                "is_checkmate": False,  
                "winner": game.winner,
                "end_reason": game.end_reason,
                "moves": moves,
            }
        )

    async def game_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "game_update",
            "board_state": event["board_state"],
            "current_turn": event["current_turn"],
            "white_time": event["white_time"],
            "black_time": event["black_time"],
            "status": event["status"],
            "is_check": event["is_check"],
            "is_checkmate": event["is_checkmate"],
            "is_stalemate": event.get("is_stalemate", False),
            "is_draw": event.get("is_draw", False),  
            "winner": event.get("winner"),
            "end_reason": event.get("end_reason"),
            "moves": event["moves"],
            "last_move": event.get("last_move"),
        }))

    @database_sync_to_async
    def get_game(self):
        try:
            return Game.objects.select_related(
                "white_player", "black_player"
            ).get(id=self.game_id)
        except Game.DoesNotExist:
            return None

    @database_sync_to_async
    def save_game(self, game):
        game.save()

    @database_sync_to_async
    def get_move_count(self):   
        return Move.objects.filter(game_id=self.game_id).count()

    @database_sync_to_async
    def save_move(self, game, player, from_square, to_square, san, move_number):
        Move.objects.create(
            game=game,
            player=player,
            from_square=from_square,
            to_square=to_square,
            san=san,
            move_number=move_number,
        )

    @database_sync_to_async
    def get_moves(self):
        moves = Move.objects.filter(
            game_id=self.game_id
        ).order_by("move_number").values(
            "id", "san", "from_square", "to_square", "move_number"
        )
        return list(moves)