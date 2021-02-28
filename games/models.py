from django.conf.urls import url
from django.db import models

# Create your models here.
from players.models import Player

class ChessGame(models.Model):
    event = models.CharField(max_length=64, blank=True, null=True)
    site = models.CharField(max_length=64, blank=True, null=True)
    date = models.CharField(max_length=64, blank=True, null=True)
    eventdate = models.CharField(max_length=64, blank=True, null=True)
    round=models.CharField(max_length=64, blank=True, null=True)
    white=models.ForeignKey("players.Player", on_delete=models.SET_NULL, blank=True, null=True, related_name='player_white')
    black=models.ForeignKey("players.Player", on_delete=models.SET_NULL, blank=True, null=True, related_name='player_black')
    result=models.CharField(max_length=10, blank=True, null=True)
    eco=models.CharField(max_length=5, blank=True, null=True)
    whiteelo=models.IntegerField(blank=True, null=True)
    blackelo=models.IntegerField(blank=True, null=True)
    video_file=models.FilePathField(path='/media/ss/BACKUP/PycharmProjects/chessShortsDjango/process/', blank=True, null=True)
    pgn=models.TextField(blank=True)

    def __str__(self):
        try:
            return f"{self.white} vs {self.black} at {self.event} on {self.date}"
        except Exception:
            return self.event



