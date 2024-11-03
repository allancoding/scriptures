import json, os

def create_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def write_file(file_path, content):
    create_directory(os.path.dirname(file_path))
    with open(file_path, "w") as f:
        f.write(json.dumps(content, indent=4))

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

volumes = read_json("complete/volumes.json")
for volume in volumes.get('volumes', []):
    books = read_json("complete/" + volume["_id"] + ".json")
    volumes["volumes"][volumes["volumes"].index(volume)] = books
    for book in books.get('books', []):
        chapters = read_json("complete/" + volume["_id"] + "/" + book["_id"] + ".json")
        books["books"][books["books"].index(book)] = chapters
        for chapter in chapters.get('chapters', []):
            verses = read_json("complete/" + volume["_id"] + "/" + book["_id"] + "/" + chapter["_id"] + ".json")
            del verses["volume"]
            del verses["book"]
            chapters["chapters"][chapters["chapters"].index(chapter)] = verses
write_file("./scriptures.json", volumes)