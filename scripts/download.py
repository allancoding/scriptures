import json, requests, os

def create_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def write_file(file_path, content):
    create_directory(os.path.dirname(file_path))
    with open(file_path, "w") as f:
        f.write(json.dumps(content, indent=4))
        
def download(urlpath, todl):
    if os.path.exists("download/" + todl + ".json"):
        return
    solditems = requests.get(urlpath)
    data = solditems.json()
    write_file("download/" + todl + ".json", data)
def read_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

urlpath = "https://openscriptureapi.org/api/scriptures/v1/lds/en/volume"

download(urlpath + "s", "volumes")

volumes = read_json("download/volumes.json")
for volume in volumes.get('volumes', []):
    download(urlpath + "/" + volume["_id"], volume["_id"])
    books = read_json("download/" + volume["_id"] + ".json")
    for book in books.get('books', []):
        download(urlpath + "/" + volume["_id"] + "/" + book["_id"], volume["_id"] + "/" + book["_id"])
        chapters = read_json("download/" + volume["_id"] + "/" + book["_id"] + ".json")
        for chapter in chapters.get('chapters', []):
            download(urlpath + "/" + volume["_id"] + "/" + book["_id"] + "/" + chapter["_id"].removeprefix(book["_id"]), volume["_id"] + "/" + book["_id"] + "/" + chapter["_id"])