import chess
import chess.pgn
import chess.svg
import sys
import cairosvg
import os
import csv

os.system("rm img/*")
os.system("rm current_game")
os.system("rm event.date")
os.system("rm event.name")
os.system("rm player-bottom.jpg")
os.system("rm player-bottom.name")
os.system("rm player-top.jpg")
os.system("rm player-top.name")

pgn = open(sys.argv[1])

while True:
    game = chess.pgn.read_game(pgn)
    game_name = f"{game.headers.get('Event','unk').replace(' ','')}_{game.headers.get('Date','unk')}_{game.headers['White'].replace(' ','')}_{game.headers['Black'].replace(' ','')}_{game.headers.get('Round','unk')}"
    board = game.board()
    player_bottom_photo=None
    player_top_photo=None

    with open('player-bottom.name', 'w') as b:
        b.write(game.headers["White"])
    with open('player-top.name', 'w') as w:
        w.write(game.headers["Black"])
    with open('event.name', 'w') as title:
        title.write(game.headers["Event"])
    with open('event.date','w') as date:
        date.write(game.headers["Date"])
    with open('current_game','w') as current:
        current.write(game_name)

    with open('player_photos.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if game.headers["White"] in row[0]:
                player_bottom_photo = row[1]
                os.system(f"cp photos/crop/{player_bottom_photo} player-bottom.jpg")
            elif game.headers["Black"] in row[0]:
                player_top_photo = row[1]
                os.system(f"cp photos/crop/{player_top_photo} player-top.jpg")

        if not player_bottom_photo:
            print("missing player_bottom_photo")
            os.system("cp photos/unknown.jpg player-bottom.jpg")
        if not player_top_photo:
            print("missing player_top_photo")
            os.system("cp photos/unknown.jpg player-top.jpg")

    for idx, move in enumerate(game.mainline_moves()):
        board.push(move)
        svg_out = chess.svg.board(board=board, lastmove=move, size=1080)
        cairosvg.svg2png(bytestring=svg_out, write_to=f'img/{idx:03d}.png')

    print("Frames generated. Processing to video with ffmpeg.")

    os.system("process_steps/frame_to_video.sh")

    print("Raw video generated. Processing to finalized video with ffmpeg.")

    os.system("process_steps/video_overlay.sh")
    print("Overlays done. Playing video.")
    with open('processed_games.csv', 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([f'{game_name}.mp4', game.headers["White"], game.headers["Black"], game.headers["Event"],game.headers["Date"]])

