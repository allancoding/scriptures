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

search = {}
volumes = read_json("complete/volumes.json")
for volume in volumes.get('volumes', []):
    books = read_json("complete/" + volume["_id"] + ".json")
    for book in books.get('books', []):
        chapters = read_json("complete/" + volume["_id"] + "/" + book["_id"] + ".json")
        current_index = 0
        for page in chapters.get('pages', []):
            current_index += 1
            search[page["_id"]] = {
                "volume": volume["title"],
                "book": book["title"],
                "page": current_index,
                "path": volume["_id"] + "/" + book["_id"] + "/" + page["_id"],
            }
        for chapter in chapters.get('chapters', []):
            current_index += 1
            search[chapter["_id"]] = {
                "volume": volume["title"],
                "book": book["title"],
                "chapter": current_index,
                "path": volume["_id"] + "/" + book["_id"] + "/" + chapter["_id"],
            }
write_file("./search.json", search)