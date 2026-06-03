#!/usr/bin/env python

import json, sys
from pathlib import Path

script_dir = Path(__file__).resolve().parent

def make_flat(input_path: Path) -> None:
    output_path = script_dir.parent / 'flat' / input_path.name.replace('.json', '-flat.json')

    with open(input_path, 'r', encoding='utf-8') as f:
        data = f.read()

    data = json.loads(data)

    verses = []
    headings = []

    def verse_reference(book_title: str, chapter_number: int, verse_number: int) -> str:
        return f'{book_title} {chapter_number}:{verse_number}'

    # Everything but D&C
    if 'books' in data:
        for b in data['books']:
            book_title = b.get('title', b.get('book', ''))

            if 'heading' in b:
                headings.append({
                    'text': b['heading'],
                    'reference': book_title,
                })

            for c in b['chapters']:
                chapter = c.get('chapter', c)
                chapter_number = chapter.get('number')

                if 'heading' in c:
                    headings.append({
                        'text': c['heading'],
                        'reference': book_title,
                    })

                for v in chapter.get('verses', []):
                    verses.append({
                        'text': v['text'],
                        'reference': verse_reference(book_title, chapter_number, v['verseNumber']),
                    })

    # D&C
    if 'sections' in data:
        for s in data['sections']:
            book_title = data.get('title', data.get('book', 'Doctrine and Covenants'))
            for v in s['verses']:
                verses.append({
                    'text': v['text'],
                    'reference': verse_reference(book_title, s.get('sectionNumber', s.get('number')), v['verseNumber']),
                })

    data = {
        'headings': headings,
        'verses': verses
    }

    if len(headings) == 0:
        del data['headings']

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)

input_dir = script_dir.parent / 'complete' / 'scriptures'

if len(sys.argv) == 1:
    input_paths = sorted(input_dir.glob('*.json'))
else:
    input_paths = [input_dir / Path(arg).name for arg in sys.argv[1:]]

for input_path in input_paths:
    make_flat(input_path)
