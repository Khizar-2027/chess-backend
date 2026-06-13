from django.urls import path
from .views import CreateMoveView, ListMovesView

urlpatterns = [
    path("", CreateMoveView.as_view(), name="create_move"),
    path("history/", ListMovesView.as_view(), name="move_history"),
 ]