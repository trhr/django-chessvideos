import os
import cairosvg
import chess.pgn, chess.svg
import ffmpeg

from games.models import ChessGame
from players.models import Player
import pathlib
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

def write_pgn_to_disk(f):
    """

    :param f: an uploaded file
    :return: the location of the file on disk
    """
    with open(f'upload/{f.name}', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        return destination.name

def read_pgn_to_board(file, game_offset=0):
    """
    :param file: the pgn file for the games
    :param game_offset: A place to seek to
    :return: a python-chess game object
    """

    with open(f'{file}', 'r') as destination:
        try:
            destination.seek(game_offset)
            return chess.pgn.read_game(destination)
        except Exception as e:
            print(f"Could not open game: {e}")

def process_game_to_images(game):
    """

    :param game: a python-chess game object
    :return: the directory the svg images are stored in
    """
    try:
        os.system("rm process/img/*")
        board = game.board()
        game_pngs = []
        for idx, move in enumerate(game.mainline_moves()):
            board.push(move)
            svg_out = chess.svg.board(board=board, lastmove=move, size=1080)
            cairosvg.svg2png(bytestring=svg_out, write_to=f'process/img/{idx:03d}.png')
            game_pngs += [f'process/img/{idx:03d}.png']
        return pathlib.Path(game_pngs[0]).parent
    except Exception as e:
        print(f"Error creating imgs: {e}")

def get_player_data_from_database(game):
    """
    [Event "Tata Steel"]
    [Site "Wijk aan Zee NED"]
    [Date "2021.01.16"]
    [EventDate "2021.01.15"]
    [Round "1"]
    [Result "1/2-1/2"]
    [White "Pentala Harikrishna"]
    [Black "Maxime Vachier-Lagrave"]
    [ECO "B90"]
    [WhiteElo "2732"]
    [BlackElo "2784"]
    [PlyCount "127"]
    :param game:
    :return: a dictionary containing game data, with players from database
    """
    try:
        black_player = Player.objects.get(aka__icontains=game.headers.get('Black'))
    except ObjectDoesNotExist:
        black_player, created = Player.objects.get_or_create(name__iexact=game.headers.get('Black'), defaults={'name': game.headers.get('Black')})

    try:
        white_player = Player.objects.get(aka__icontains=game.headers.get('White'))
    except ObjectDoesNotExist:
        white_player, created = Player.objects.get_or_create(name__iexact=game.headers.get('White'), defaults={'name': game.headers.get('White')})


    game_data = {
        'event': game.headers.get('Event', 'unk'),
        'site': game.headers.get('Site', 'unk'),
        'date': game.headers.get('Date', 'unk'),
        'eventdate': game.headers.get('EventDate','unk'),
        'round': game.headers.get('Round', 'unk'),
        'result': game.headers.get('Result', 'unk'), #TODO: Process result
        'white': white_player,
        'black': black_player,
        'eco': game.headers.get('ECO', 'unk'),
        'whiteelo': game.headers.get('WhiteElo', 'unk'),
        'blackelo': game.headers.get('BlackElo', 'unk'),
        'pgn': game.accept(chess.pgn.StringExporter(headers=True, variations=False, comments=False)),
    }
    return game_data


def create_overlay_video(game_images_dir, game_data):
    """

    :param game_images_dir: the directory game images are stored in
    :param game_data: the game header content
    :return:
    """
    try:
        path, dirs, files = next(os.walk(game_images_dir))
        duration = len(files)
        game_video = ffmpeg.input(f'{game_images_dir}/*.png', pattern_type='glob', framerate=1).filter('fps', fps=30, round='up')

        top_image = (
            ffmpeg.input(f"{game_data.get('black').photo.file if game_data.get('black').photo else 'media/unknown.jpg'}")
        )
        bottom_image = (
            ffmpeg.input(f"{game_data.get('white').photo.file if game_data.get('white').photo else 'media/unknown.jpg'}")
        )
        output_filename = f"{game_data.get('event').replace(' ', '')}_{game_data.get('date').replace('?', '')}_{game_data.get('white').name.replace(' ', '')}_{game_data.get('black').name.replace(' ', '')}_{game_data.get('round')}.mp4"
        output_file = f"process/{output_filename}"
        (
            ffmpeg
            .input('process/templates/background.png')
            .overlay(top_image)
            .overlay(game_video, x=0, y=420)
            .overlay(bottom_image, x=660, y=1500)
            .drawbox(x=0, y=0, width=420, height=420, color="black@0.5", thickness=5)
            .drawbox(x=660, y=1500, width=420, height=420, color="black@0.5", thickness=5)
            .drawbox(x=0, y=420, width=1080, height=1080, color="black@0.5", thickness=8)
            .drawtext(fontfile='/home/ss/.local/share/fonts/nevis.ttf', text=game_data.get('event'), fontsize=66, fontcolor='ffffff', x='(1080-text_w)/2', y='((1920-text_h)/2)-28', bordercolor='black', borderw=2, alpha='if(lt(t,0),0,if(lt(t,2),(t-0)/2,if(lt(t,6),1,if(lt(t,8),(2-(t-6))/2,0))))')
            .drawtext(fontfile='/home/ss/.local/share/fonts/nevis.ttf', text=game_data.get('date'), fontsize=66, fontcolor='cccccc', x='(1080-text_w)/2', y='((1920-text_h)/2)+28', bordercolor='black', borderw=2, alpha='if(lt(t,0),0,if(lt(t,2),(t-0)/2,if(lt(t,6),1,if(lt(t,8),(2-(t-6))/2,0))))')
            .drawtext(fontfile='/home/ss/.local/share/fonts/nevis.ttf', text=game_data.get('black').name, fontsize=45, fontcolor='ffffff', x=500, y=210)
            .drawtext(fontfile='/home/ss/.local/share/fonts/nevis.ttf', text=game_data.get('white').name, fontsize=45, fontcolor='ffffff', x='1080-500-text_w', y=1710)
            .drawtext(fontfile='/home/ss/.local/share/fonts/nevis.ttf', text=game_data.get('result'), fontsize=90, fontcolor='000000', x='(1080-text_w)/2', y='(1920-text_h)/2', bordercolor='white', borderw=6, enable=f'between(t,{duration-6},{duration})')
            .output(output_file)
            .overwrite_output()
            .run()
        )

        return settings.BASE_DIR / output_file
    except Exception as e:
        print(f"Error creating game video: {e}")
        return False


def split_pgn(file):
    """

    :param file: an imported file
    :return: A list offsets
    """
    game_list=[]
    with open(f'{file}', 'r') as destination:
        try:
            while True:
                offset = destination.tell()
                headers = chess.pgn.read_headers(destination)
                if headers is None:
                    break
                game_list += [(offset, headers)]

        except Exception as e:
            print(f"Could not open game: {e}")
        return game_list

def process_pgn(f):
    file = write_pgn_to_disk(f)
    offsets = split_pgn(file)
    for offset, headers in offsets:
        game = read_pgn_to_board(file, game_offset=offset)
        game_data = get_player_data_from_database(game)
        try:
            game_data['whiteelo'] = int(game_data['whiteelo'])
        except Exception:
            game_data['whiteelo'] = None
        try:
            game_data['blackelo'] = int(game_data['blackelo'])
        except Exception:
            game_data['blackelo'] = None

        dbpush = push_to_database(game_data)

        #image_dir = process_game_to_images(game)
        #video_filename = create_overlay_video(image_dir, game_data)
        #video_filenames += [video_filename]
        #game_data['video_file'] = video_filename
        #cleanup()
    return dbpush

def push_to_database(game_data):
    game = ChessGame(**game_data)
    game.save()
    return game

def cleanup():
    os.system("rm process/img/*")

