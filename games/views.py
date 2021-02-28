import cairosvg as cairosvg
from django.http import HttpResponseRedirect
from django.shortcuts import render
from players.models import Player
from .forms import UploadGameForm
from . import utils
# Create your views here.



def UploadGame(request):
    if request.method == 'POST':
        form = UploadGameForm(request.POST, request.FILES)
        if form.is_valid():
            utils.process_pgn(request.FILES['game'])
            return HttpResponseRedirect('/upload/')
    else:
        form=UploadGameForm()
    return render(request, 'upload.html', {'form': form})
