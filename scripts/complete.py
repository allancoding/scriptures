import json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

SCRIPTURES_SOURCE = os.path.join(ROOT_DIR, "scriptures")
STUDY_HELPS_SOURCE = os.path.join(ROOT_DIR, "study-helps")
COMPLETE_ROOT = os.path.join(ROOT_DIR, "complete")

def join_path(*parts):
    return os.path.join(*parts)

def slugify(value):
    if not isinstance(value, str):
        return ""

    return (
        value.strip()
        .lower()
        .replace("/", "-")
        .replace(" ", "-")
    )

def create_directory(directory_path):
    if directory_path and not os.path.exists(directory_path):
        os.makedirs(directory_path)

def write_file(file_path, content):
    create_directory(os.path.dirname(file_path))
    with open(file_path, "w", encoding="utf-8") as file_handle:
        file_handle.write(json.dumps(content, indent=4, ensure_ascii=False))

def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)

def chapter_folder_name(book_detail):
    chapter_delineation = book_detail.get("chapterDelineation")
    if isinstance(chapter_delineation, str) and chapter_delineation.strip():
        folder_name = slugify(chapter_delineation)
    else:
        folder_name = "chapters"

    if not folder_name.endswith("s"):
        folder_name += "s"

    return folder_name

def build_scriptures_complete():
    volumes_index = read_json(join_path(SCRIPTURES_SOURCE, "volumes.json"))

    for volume_index, volume in enumerate(volumes_index.get("volumes", [])):
        volume_id = volume.get("_id")
        volume_name = slugify(volume.get("title"))
        if not volume_id or not volume_name:
            continue

        volume_source_dir = join_path(SCRIPTURES_SOURCE, volume_id)
        volume_detail = read_json(join_path(volume_source_dir, "volume.json"))
        volumes_index["volumes"][volume_index] = volume_detail

        for book_index, book in enumerate(volume_detail.get("books", [])):
            book_id = book.get("_id")
            if not book_id:
                continue

            book_source_dir = join_path(volume_source_dir, book_id)
            book_detail = read_json(join_path(book_source_dir, "book.json"))
            volume_detail["books"][book_index] = book_detail

            chapter_dir_name = chapter_folder_name(book_detail)
            chapter_source_dir = join_path(book_source_dir, chapter_dir_name)

            for chapter_index, chapter in enumerate(book_detail.get("chapters", [])):
                chapter_id = chapter.get("_id")
                if not chapter_id:
                    continue

                chapter_detail = read_json(join_path(chapter_source_dir, chapter_id + ".json"))
                chapter_detail.pop("volume", None)
                chapter_detail.pop("book", None)
                book_detail["chapters"][chapter_index] = chapter_detail

        write_file(join_path(COMPLETE_ROOT, "scriptures", volume_name + ".json"), volume_detail)

    return volumes_index

def build_study_helps_complete():
    types_index = read_json(join_path(STUDY_HELPS_SOURCE, "types.json"))

    for type_index, type_item in enumerate(types_index.get("types", [])):
        type_name = type_item.get("type")
        if not type_name:
            continue

        type_source_dir = join_path(STUDY_HELPS_SOURCE, type_name)
        entries_detail = read_json(join_path(type_source_dir, "entries.json"))
        types_index["types"][type_index] = entries_detail

        for entry_index, entry in enumerate(entries_detail.get("entries", [])):
            entry_id = entry.get("_id") or entry.get("entryId")
            if not entry_id:
                continue

            entry_detail = read_json(join_path(type_source_dir, "entries", entry_id + ".json"))
            entries_detail["entries"][entry_index] = entry_detail

        write_file(join_path(COMPLETE_ROOT, "study-helps", type_name + ".json"), entries_detail)

    return types_index

scriptures = build_scriptures_complete()
study_helps = build_study_helps_complete()

write_file(join_path(COMPLETE_ROOT, "scriptures.json"), scriptures)
write_file(join_path(COMPLETE_ROOT, "study-helps.json"), study_helps)
