from rest_framework import serializers
from .models import *


class FileNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = DropboxFiles
        fields = "__all__"

