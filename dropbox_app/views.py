from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from .serializer import *
from rest_framework.generics import *
from rest_framework.response import Response
from rest_framework import status
import os
import dropbox
import dropbox.files
import hashlib
import concurrent.futures
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser


with open(r"C:\Users\Vrdella\Desktop\django_projects\dropbox_project\dropbox\token.txt", 'r') as f:
    token = f.read()
db = dropbox.Dropbox(token)


def upload(file_path):
    # Extract the file name from the provided file path
    file_name = os.path.basename(file_path)

    # Read the file data
    with open(file_path, "rb") as f:
        data = f.read()

    # Perform the upload with the file name
    db.files_upload(data, f"/{file_name}")
    return file_name


# Create your views here.
def index(request):
    return HttpResponse("hello world")


class DropboxDownloadAPI(APIView):
    def post(self, request, *args, **kwargs):
        try:
            file_names = []
            for entry in db.files_list_folder("").entries:
                db.files_download_to_file(os.path.join("dropbox_app/downloaded_files", entry.name), f"/{entry.name}")
                file_names.append(entry.name)
            if file_names:
                data = {
                    'Response Code': status.HTTP_201_CREATED,
                    'Status': 'TRUE',
                    'Message': 'Data Downloaded Successfully',
                    "Error": 'None',
                    'Data': {'Downloded_Files': file_names},
                }
                return Response(data)
        except Exception as e:
            data = {
                'Response Code': status.HTTP_201_CREATED,
                'Status': 'TRUE',
                'Message': 'No data is available',
                "Error": str(e),
                'Data': [],
            }
            return Response(data)


class UploadDropboxAPI(CreateAPIView):
    parser_classes = (MultiPartParser,)
    serializer_class = FileNameSerializer

    def post(self, request, *args, **kwargs):
        try:
            files = request.FILES.getlist('file_name')
            serialized_files = []
            count = []
            for file in files:
                data = {'file_name': file}
                serializer = FileNameSerializer(data=data)
                if serializer.is_valid():
                    saved_instance = serializer.save()
                    serialized_files.append({
                        'pdf': saved_instance.file_name.path,
                        'id': saved_instance.id
                    })
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        futures = [executor.submit(upload, saved_instance.file_name.path)]
                        for i in futures:
                            count.append(i.result())

                        concurrent.futures.wait(futures)
            data = {
                'Response Code': status.HTTP_201_CREATED,
                'Status': 'TRUE',
                'Message': 'Data Uploaded Successfully',
                "Error": 'None',
                'Data': {'Uploaded_Files': count},
            }
            return Response(data)
        except Exception as e:
            data = {
                'Response Code': status.HTTP_201_CREATED,
                'Status': 'TRUE',
                'Message': 'No data is available',
                "Error": str(e),
                'Data': [],
            }
            return Response(data)