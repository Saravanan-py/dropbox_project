from django.db import models


# Create your models here.
class DropboxFiles(models.Model):
    file_name = models.FileField()