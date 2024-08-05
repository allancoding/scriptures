import json, os, re

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

def split_string(input_string):
    split_pattern = r"; (?=[A-Z])"
    return re.split(split_pattern, input_string)

def contains_any(string, substrings):
    return any(substring in string for substring in substrings)

def split_after_first_delimiter(input_string):
    match = re.search(r'(?<!v)[.;]', input_string)
    if match:
        return input_string[match.start()+1:]
    else:
        return input_string

footnote = {}
valid_books = [
    "1\u00a0Chr.", "1\u00a0Cor.", "1\u00a0Jn.", "1\u00a0Kgs.", "1\u00a0Pet.", "1\u00a0Sam.", "1\u00a0Thes.", "1\u00a0Tim.",
    "2\u00a0Chr.", "2\u00a0Cor.", "2\u00a0Kgs", "2\u00a0Ne.", "2\u00a0Pet.", "2\u00a0Sam.", "2\u00a0Thes.", "2\u00a0Tim.",
    "3\u00a0Jn.", "3\u00a0Ne.", "4\u00a0Ne.",
    "A\u00a0of\u00a0F", "Acts", "Alma", "Amos", "Abr.", "Col.", "Dan.", "Deut.", "D&C", "Eph.",
    "Ether", "Eccl.", "Esth.", "Ezra", "Ezek.", "Gal.", "Gen.", "Hag.", "Hab.", "Hel.",
    "Heb.", "Hosea", "Isa.", "Jacob", "James", "Jer.", "Job", "Joel", "Jonah", "JS—H",
    "JS—M", "Judg.", "Jude", "Lam.", "Lev.", "Luke", "Mal.", "Mark", "Micah", "Moro.",
    "Mosiah", "Num.", "Nahum", "Neh.", "Obad.", "Omni", "Philip.", "Philem.", "Prov.",
    "Ps.", "Ruth", "Rom.", "Song", "Titus", "W\u00a0of\u00a0M", "Zech.", "Zeph.",
]
ivalid_books = ["JST\u00a0Ex.", "JST\u00a0Rev.", "JST\u00a0Jer."]
volumes = read_json("complete/volumes.json")
for volume in volumes.get('volumes', []):
    books = read_json("complete/" + volume["_id"] + ".json")
    for book in books.get('books', []):
        chapters = read_json("complete/" + volume["_id"] + "/" + book["_id"] + ".json")
        for chapter in chapters.get('chapters', []):
            verses = read_json("complete/" + volume["_id"] + "/" + book["_id"] + "/" + chapter["_id"] + ".json")
            for verse in verses["chapter"].get('verses', []):
                for footnotes in verse.get('footnotes', []):
                    footnotes = footnotes["footnote"]
                    if contains_any(footnotes, valid_books) and not contains_any(footnotes, ivalid_books):
                        setLink = True
                        if footnotes.startswith("IE\u00a0"):
                            strip = split_after_first_delimiter(footnotes)
                            if strip.strip():
                                fnote = strip.lstrip().split(". TG", 1)[0].lstrip().removeprefix("See ").removeprefix("see ")
                                cutup = [part.strip() for part in fnote.split(";") if any(part.strip().startswith(prefix) for prefix in valid_books)]
                                if not cutup:
                                    setLink = False
                                else:
                                    print(cutup)
                        footnote[footnotes] = {
                            "link": setLink
                        }
                    elif footnotes.startswith("TG\u00a0") or footnotes.startswith("IE\u00a0") or footnotes.startswith("GR\u00a0") or footnotes.startswith("BD\u00a0") or footnotes.startswith("OR\u00a0") or footnotes.startswith("HEB\u00a0"):
                        footnote[footnotes] = { "link": False}
                    else:
                        footnote[footnotes] = {}
write_file("./footnote.json", footnote)