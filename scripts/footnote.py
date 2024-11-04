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

def split_string(input_string, valid_strings):
    input_string = input_string.removeprefix("See ")
    input_string = re.sub(r";\s*see\s*", "; ", input_string)
    valid_strings_pattern = '|'.join(re.escape(s[0]) for s in valid_strings)
    split_pattern = rf"; (?=(?:{valid_strings_pattern}))"
    parts = re.split(split_pattern, input_string)
    return [part.strip() for part in parts]

def vaid_contains_any(string, substrings):
    return any(substring[0] in string for substring in substrings)

def contains_any(string, substrings):
    return any(substring in string for substring in substrings)

def starts_any(string, substrings):
    return any(string.startswith(substring) for substring in substrings)

def split_at_last_period(string):
    match = re.search(r'(?<![a-zA-Z])\.(?!.*(?<![a-zA-Z])\.)', string)
    if match:
        return [string[:match.start()], string[match.start()+1:].strip()]
    return [string]

def not_valid_fun(footnotes):
    type = re.split(r'\u00a0|\xa0', footnotes, 1)[0]
    return {
        "link": True,
        "type": type
    }

def split_after_first_delimiter(input_string):
    match = re.search(r'(?<!v)[.;]', input_string)
    if match:
        return input_string[match.start()+1:]
    else:
        return input_string

footnote = {}
valid_books = [
    ["1\u00a0Chr.", "oldtestament/1chronicles"],
    ["1\u00a0Cor.", "newtestament/1corinthians"],
    ["1\u00a0Jn.", "newtestament/1john"],
    ["1\u00a0Ne.", "bookofmormon/1nephi"],
    ["1\u00a0Kgs.", "oldtestament/1kings"],
    ["1\u00a0Pet.", "newtestament/1peter"],
    ["1\u00a0Sam.", "oldtestament/1samuel"],
    ["1\u00a0Thes.", "newtestament/1thessalonians"],
    ["1\u00a0Tim.", "newtestament/1timothy"],
    ["2\u00a0Chr.", "oldtestament/2chronicles"],
    ["2\u00a0Cor.", "newtestament/2corinthians"],
    ["2\u00a0Kgs", "oldtestament/2kings"],
    ["2\u00a0Ne.", "bookofmormon/2nephi"],
    ["2\u00a0Pet.", "newtestament/2peter"],
    ["2\u00a0Sam.", "oldtestament/2samuel"],
    ["2\u00a0Thes.", "newtestament/2thessalonians"],
    ["2\u00a0Tim.", "newtestament/2timothy"],
    ["2\u00a0Jn.", "newtestament/2john"],
    ["3\u00a0Jn.", "newtestament/3john"],
    ["3\u00a0Ne.", "bookofmormon/3nephi"],
    ["4\u00a0Ne.", "bookofmormon/4nephi"],
    ["A\u00a0of\u00a0F", "pearlofgreatprice/articlesoffaith"],
    ["Acts", "newtestament/acts"],
    ["Alma", "bookofmormon/alma"],
    ["Amos", "oldtestament/amos"],
    ["Abr.", "pearlofgreatprice/abraham"],
    ["Col.", "newtestament/colossians"],
    ["Dan.", "oldtestament/daniel"],
    ["Deut.", "oldtestament/deuteronomy"],
    ["D&C", "doctrineandcovenants"],
    ["Eph.", "newtestament/ephesians"],
    ["Ether", "bookofmormon/ether"],
    ["Eccl.", "oldtestament/ecclesiastes"],
    ["Enos", "bookofmormon/enos"],
    ["Esth.", "oldtestament/esther"],
    ["Ex.", "oldtestament/exodus"],
    ["Ezra", "oldtestament/ezra"],
    ["Ezek.", "oldtestament/ezekiel"],
    ["Gal.", "newtestament/galatians"],
    ["Gen.", "oldtestament/genesis"],
    ["Hag.", "oldtestament/haggai"],
    ["Hab.", "oldtestament/habakkuk"],
    ["Hel.", "bookofmormon/helaman"],
    ["Heb.", "newtestament/hebrews"],
    ["Hosea", "oldtestament/hosea"],
    ["Isa.", "oldtestament/isaiah"],
    ["Jacob", "bookofmormon/jacob"],
    ["James", "newtestament/james"],
    ["Jer.", "oldtestament/jeremiah"],
    ["Job", "oldtestament/job"],
    ["Joel", "oldtestament/joel"],
    ["Jonah", "oldtestament/jonah"],
    ["JS—H", "pearlofgreatprice/josephsmithhistory"],
    ["John", "newtestament/john"],
    ["Josh.", "oldtestament/joshua"],
    ["Jarom", "bookofmormon/jarom"],
    ["JS—M", "pearlofgreatprice/josephsmithmatthew"],
    ["Judg.", "oldtestament/judges"],
    ["Jude", "newtestament/jude"],
    ["Lam.", "oldtestament/lamentations"],
    ["Lev.", "oldtestament/leviticus"],
    ["Luke", "newtestament/luke"],
    ["Mal.", "oldtestament/malachi"],
    ["Mark", "newtestament/mark"],
    ["Matt.", "newtestament/matthew"],
    ["Micah", "oldtestament/micah"],
    ["Moro.", "bookofmormon/moroni"],
    ["Morm.", "bookofmormon/mormon"],
    ["Mosiah", "bookofmormon/mosiah"],
    ["Moses", "pearlofgreatprice/moses"],
    ["Num.", "oldtestament/numbers"],
    ["Nahum", "oldtestament/nahum"],
    ["Neh.", "oldtestament/nehemiah"],
    ["Obad.", "oldtestament/obadiah"],
    ["Omni", "bookofmormon/omni"],
    ["Philip.", "newtestament/philippians"],
    ["Philem.", "newtestament/philemon"],
    ["Prov.", "oldtestament/proverbs"],
    ["Ps.", "oldtestament/psalms"],
    ["Ruth", "oldtestament/ruth"],
    ["Rom.", "newtestament/romans"],
    ["Rev.", "newtestament/revelation"],
    ["Song", "oldtestament/songofsolomon"],
    ["Titus", "newtestament/titus"],
    ["W\u00a0of\u00a0M", "bookofmormon/wordsofmormon"],
    ["Zech.", "oldtestament/zechariah"],
    ["Zeph.", "oldtestament/zephaniah"],
]
ivalid_books = ["JST\u00a0Ex.", "JST\u00a0Rev.", "JST\u00a0Jer."]
not_valid_books = ["TG\u00a0", "IE\u00a0", "GR\u00a0", "BD\u00a0", "OR\u00a0", "HEB\u00a0", "TG\xa0", "IE\xa0", "GR\xa0", "BD\xa0", "OR\xa0", "HEB\xa0"]
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
                    if vaid_contains_any(footnotes, valid_books):
                        cut_footnotes = split_at_last_period(footnotes)
                        list_footnotes = split_string(cut_footnotes[0], valid_books + ([[item] for item in not_valid_books]))
                        links = []
                        # if len(cut_footnotes) > 1 and cut_footnotes[1]:
                        #     list_footnotes.append(cut_footnotes[1])
                        for note in list_footnotes:
                            # print(note)
                            notes = []
                            if starts_any(note, ivalid_books) or starts_any(note, not_valid_books):
                                notes.append(note)
                            else:
                                notes.append(note)
                                notes.append("path")
                            links.append(notes)
                        footnote[footnotes] = {
                            "link": True,
                            "links": links
                        }
                    elif starts_any(footnotes, not_valid_books):
                        footnote[footnotes] = not_valid_fun(footnotes)
                    else:
                        footnote[footnotes] = { "link": False }
write_file("./footnote.json", footnote)

print(split_string(split_at_last_period("HEB\u00a0shaped, fashioned, created; always divine activity; see Abr. 4:1, organized, formed. TG\u00a0Creation; God, Creator.")[0], valid_books))