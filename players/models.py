from django.db import models

# Create your models here.

class Player(models.Model):
    name=models.CharField(max_length=64, unique=True)
    aka=models.TextField(blank=True)
    photo=models.ImageField(blank=True, null=True)
    photo_attrib=models.TextField(blank=True)

    class Meta:
        ordering=['name']

    def __str__(self):
        return self.name