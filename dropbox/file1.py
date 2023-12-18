import os
import dropbox
import dropbox.files
import hashlib

with open("token.txt", 'r') as f:
    token = f.read()

db = dropbox.Dropbox(token)


def upload():
    for file in os.listdir('local_files'):
        with open(os.path.join("local_files", file), "rb") as f:
            data = f.read()
            db.files_upload(data, f"/{file}")


def download():
    for entry in db.files_list_folder("").entries:
        db.files_download_to_file(os.path.join("local_files", entry.name), f"/{entry.name}")


# download()


def content_hash(file):
    hash_chunk_size = 4 * 1024 * 1024
    with open(file, "rb") as f:
        block_hashes = bytes()
        while True:
            chunk = f.read(hash_chunk_size)
            if not chunk:
                break
            block_hashes += hashlib.sha256(chunk).digest()
        return hashlib.sha256(block_hashes).hexdigest()


def download_changed():
    for entry in db.files_list_folder("").entries:
        if os.path.exists(os.path.join("local_files", entry.name)):
            local_hash = content_hash(os.path.join("local_files", entry.name))
            if local_hash != entry.content_hash:
                print("File has Changed:", entry.name)
                db.files_download_to_file(os.path.join("local_files", entry.name), f"/{entry.name}")
            else:
                print("Unchanged:", entry.name)
        else:
            print("New File", entry.name)
            db.files_download_to_file(os.path.join("local_files", entry.name), f"/{entry.name}")


def upload_changed():
    cloud_files = {e.name: e.content_hash for e in db.files_list_folder("").entries}
    for file in os.listdir("local_files"):
        if file in cloud_files.keys():
            local_hash = content_hash(os.path.join("local_files", file))
            if local_hash != cloud_files[file]:
                print("File Changed:", file)
                with open(os.path.join("local_files", file), "rb") as f:
                    data = f.read()
                    db.files_upload(data, f"/{file}", mode=dropbox.files.WriteMode("overwrite"))
            else:
                print("Unchanged:", file)
        else:
            print("New File:", file)
            with open(os.path.join("local_files", file), "rb") as f:
                data = f.read()
                db.files_upload(data, f"/{file}", mode=dropbox.files.WriteMode("overwrite"))


with open(os.path.join(r"C:\Users\Vrdella\Downloads\MOCK_DATA.json"), "r") as f:
    data = f.read()
print(data)
