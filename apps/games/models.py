from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Game(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('active', 'Active'),
        ('finished', 'Finished')
    ]

    white_player = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='white_games'
    )

    black_player = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='black_games',
        null=True,
        blank=True,
    )

    white_time = models.IntegerField(default=600)
    black_time = models.IntegerField(default=600)
    last_move_time = models.DateTimeField(auto_now=True)

    current_turn = models.CharField(
        max_length=5,
        default="white",
    )

    board_state = models.TextField(
        default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",  
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='waiting'
    )

    winner = models.CharField(
        max_length=10,
        null=True,
        blank=True,
    )

    end_reason = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Game {self.id} - {self.status}"