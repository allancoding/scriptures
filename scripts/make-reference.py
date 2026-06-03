#!/usr/bin/env python

from collections import OrderedDict
import json, sys
from pathlib import Path

script_dir = Path(__file__).resolve().parent

def make_reference(input_path: Path) -> None:
    output_filename = input_path.name.replace('.json', '')
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    output = OrderedDict()

    # Everything but D&C
    if 'books' in data:
        for b in data['books']:
            # Use the human title as the key (e.g. "1 Nephi")
            book_key = b.get('title', b.get('titleShort', b.get('_id', '')))
            if book_key == '':
                continue

            if book_key not in output:
                output[book_key] = OrderedDict()

            if 'heading' in b:
                output[book_key]['heading'] = b['heading']

            for c in b.get('chapters', []):
                chapter = c.get('chapter', c)
                chapter_number = chapter.get('number')
                chapter_key = str(chapter_number) if chapter_number is not None else str(c.get('_id', ''))

                if chapter_key not in output[book_key]:
                    output[book_key][chapter_key] = OrderedDict()

                if 'heading' in c:
                    output[book_key][chapter_key]['heading'] = c['heading']

                for v in chapter.get('verses', []):
                    verse_num = v.get('verseNumber') or v.get('verse')
                    if verse_num is None:
                        continue
                    output[book_key][chapter_key][str(verse_num)] = v.get('text', '')

    # D&C / sections
    if 'sections' in data:
        for s in data['sections']:
            section_number = s.get('sectionNumber') or s.get('number') or s.get('_id')
            section_key = str(section_number)

            if section_key not in output:
                output[section_key] = OrderedDict()

            for v in s.get('verses', []):
                verse_num = v.get('verseNumber') or v.get('verse')
                if verse_num is None:
                    continue
                output[section_key][str(verse_num)] = v.get('text', '')

    out_dir = script_dir.parent / 'reference'
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{output_filename}-reference.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, sort_keys=False, indent=4, ensure_ascii=False)


input_dir = script_dir.parent / 'complete' / 'scriptures'

if len(sys.argv) == 1:
    input_paths = sorted(input_dir.glob('*.json'))
else:
    input_paths = [input_dir / Path(arg).name for arg in sys.argv[1:]]

for input_path in input_paths:
    make_reference(input_path)
