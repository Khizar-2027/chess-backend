from django.urls import path, include
from .views import CreateGameView, JoinGameView, GameListView, GameDetailView, MyGamesView, ResignGameView, FinishedGamesView

urlpatterns = [
    path('', GameListView.as_view(), name="game_list"),
    path('create/', CreateGameView.as_view(), name="create_game"),
    path('join/<int:pk>/', JoinGameView.as_view(), name="join_game"),
    path('my/', MyGamesView.as_view(), name="my_games"),      
    path('<int:pk>/', GameDetailView.as_view(), name="game_detail"),
    path('<int:pk>/resign/', ResignGameView.as_view(), name="resign_game"),
    path('<int:game_id>/move/', include("apps.moves.urls")),
    path("finished/", FinishedGamesView.as_view(), name="finished-games"),
]