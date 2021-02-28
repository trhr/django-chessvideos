from django import forms

class UploadGameForm(forms.Form):
    game=forms.FileField()