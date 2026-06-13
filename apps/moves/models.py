from django.db import models
from apps.games.models import Game
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Move(models.Model):

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='moves'
    )

    player = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    from_square = models.CharField(max_length=2)
    to_square = models.CharField(max_length=2)

    san = models.CharField(
        max_length=20,
        blank=True,
        )
    move_number = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.move_number}. {self.from_square} -> {self.to_square}"
