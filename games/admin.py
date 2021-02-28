from django.contrib import admin

# Register your models here.
from django.urls import reverse
from django.utils.html import format_html

from games.models import ChessGame
from games import utils


@admin.register(ChessGame)
class ChessGameAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'white_link',
        'black_link',
        'event',
        'date',
        'round',
        'result',
        'white_photo',
        'black_photo',
        'video_file',
    )

    list_filter = (
        'event', 'white', 'black', 'date'
    )

    actions = ['create_video']

    def white_link(self, obj):
        url = reverse('admin:players_player_change', args=[obj.white.id])
        return format_html("<a href='{}'>{}</a>", url, obj.white)

    def black_link(self, obj):
        url = reverse('admin:players_player_change', args=[obj.black.id])
        return format_html("<a href='{}'>{}</a>", url, obj.black)

    def white_photo(self, obj):
        return obj.white.photo

    def black_photo(self, obj):
        return obj.black.photo

    def create_video(self, request, queryset):
        import chess.pgn, io

        for gameobj in queryset:
            game_data = {
                'event': gameobj.event,
                'site': gameobj.site,
                'date': gameobj.date,
                'eventdate': gameobj.eventdate,
                'round': gameobj.round,
                'result': gameobj.result,  # TODO: Process result
                'white': gameobj.white,
                'black': gameobj.black,
                'eco': gameobj.eco,
                'whiteelo': gameobj.whiteelo,
                'blackelo': gameobj.blackelo,
                'pgn': gameobj.pgn,
            }

            game = chess.pgn.read_game(io.StringIO(gameobj.pgn))
            image_dir = utils.process_game_to_images(game)
            video_file = utils.create_overlay_video(image_dir, game_data)
            gameobj.video_file = video_file
            gameobj.save()

    create_video.short_description = "Create a video from this game's PGN"
