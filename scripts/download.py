#!/usr/bin/env python3
"Download the Open Scripture API into a local JSON."

import argparse, json, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent

BASE_URL = "https://openscriptureapi.org/api"
SCRIPTURES_BASE = f"{BASE_URL}/scriptures/v1/lds/en"
STUDY_HELPS_BASE = f"{BASE_URL}/study-helps/v1/lds/en"
DEFAULT_OUTPUT_DIR = ROOT_DIR
RECENT_DOWNLOAD_DAYS = 30

if str(ROOT_DIR) not in sys.path:
	sys.path.insert(0, str(ROOT_DIR))

try:
	from urllib.request import Request, urlopen
	from urllib.error import URLError, HTTPError
except Exception:
	Request = None

def build_request_headers() -> dict[str, str]:
	return {"User-Agent": "scriptures-downloader/1.0"}

def fetch_json(url: str, headers: dict[str, str] | None = None, timeout: int = 30) -> tuple[int, object]:
	headers = headers or {}
	try:
		req = Request(url, headers=headers)
		with urlopen(req, timeout=timeout) as fh:
			content = fh.read()
			try:
				payload = json.loads(content.decode("utf-8"))
			except Exception:
				payload = content.decode("utf-8", errors="replace")
			status = getattr(fh, "status", 200)
			return int(status), payload
	except HTTPError as he:
		try:
			body = he.read().decode("utf-8", errors="replace")
		except Exception:
			body = str(he)
		return he.code or 0, body
	except URLError as ue:
		return 0, str(ue)
	except Exception as exc:
		return 0, str(exc)

def print_request_failure(status: int, payload: object) -> None:
	print("Request failed:", status, file=sys.stderr)
	try:
		print(json.dumps(payload, indent=2, ensure_ascii=False), file=sys.stderr)
	except Exception:
		print(str(payload), file=sys.stderr)
	sys.exit(1)

def ensure_dir(path: Path) -> None:
	path.mkdir(parents=True, exist_ok=True)

def slugify(value: str) -> str:
	value = value.strip().lower()
	value = value.replace("/", "-")
	value = value.replace(" ", "-")
	return "".join(ch for ch in value if ch.isalnum() or ch in {"-", "_"})


def name_or_id(item: dict[str, Any], key: str = "title") -> str:
	value = item.get(key) if isinstance(item, dict) else None
	if isinstance(value, str) and value.strip():
		return value
	identifier = item.get("_id") if isinstance(item, dict) else None
	return identifier if isinstance(identifier, str) else "unknown"

def chapter_folder_name(book_detail: dict[str, Any]) -> str:
	chapter_delineation = book_detail.get("chapterDelineation") if isinstance(book_detail, dict) else None
	folder_name = slugify(chapter_delineation) if isinstance(chapter_delineation, str) and chapter_delineation.strip() else "chapters"
	if not folder_name.endswith("s"):
		folder_name = f"{folder_name}s"
	return folder_name

def write_json(path: Path, payload: Any) -> None:
	ensure_dir(path.parent)
	path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

def ensure_dir(path: Path) -> None:
	path.mkdir(parents=True, exist_ok=True)

def slugify(value: str) -> str:
	value = value.strip().lower()
	value = value.replace("/", "-")
	value = value.replace(" ", "-")
	return "".join(ch for ch in value if ch.isalnum() or ch in {"-", "_"})

def name_or_id(item: dict[str, Any], key: str = "title") -> str:
	value = item.get(key) if isinstance(item, dict) else None
	if isinstance(value, str) and value.strip():
		return value
	identifier = item.get("_id") if isinstance(item, dict) else None
	return identifier if isinstance(identifier, str) else "unknown"

def chapter_folder_name(book_detail: dict[str, Any]) -> str:
	chapter_delineation = book_detail.get("chapterDelineation") if isinstance(book_detail, dict) else None
	folder_name = slugify(chapter_delineation) if isinstance(chapter_delineation, str) and chapter_delineation.strip() else "chapters"
	if not folder_name.endswith("s"):
		folder_name = f"{folder_name}s"
	return folder_name

def write_json(path: Path, payload: Any) -> None:
	ensure_dir(path.parent)
	path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

def is_recent(path: Path, days: int = RECENT_DOWNLOAD_DAYS) -> bool:
	if not path.exists():
		return False
	try:
		age = datetime.now(timezone.utc) - datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
		return age <= timedelta(days=days)
	except Exception:
		return False

def read_json_file(path: Path) -> Any:
	return json.loads(path.read_text(encoding="utf-8"))

def fetch_or_load_json(
	url: str,
	path: Path,
	*,
	fatal: bool = True,
) -> tuple[Any, bool]:
	if is_recent(path):
		try:
			return read_json_file(path), True
		except Exception:
			pass

	payload = fetch(url, fatal=fatal)
	write_json(path, payload)
	return payload, False

def fetch(url: str, retries: int = 3, timeout: int = 30, backoff_factor: float = 1.5, fatal: bool = True) -> Any:
	attempt = 0
	while True:
		attempt += 1
		try:
			status, payload = fetch_json(url, headers=build_request_headers(), timeout=timeout)
		except Exception as exc:
			if attempt >= retries:
				if fatal:
					print_request_failure(0, str(exc))
				return {} if not fatal else None  # unreachable when fatal True
			sleep = backoff_factor * (2 ** (attempt - 1))
			time.sleep(sleep)
			continue

		if status == 200:
			return payload

		if 500 <= status < 600 and attempt < retries:
			sleep = backoff_factor * (2 ** (attempt - 1))
			time.sleep(sleep)
			continue

		if fatal:
			print_request_failure(status, payload)
		return {} if not fatal else None

def fetch_verse_detail(book_id: str, chapter_number: int, verse_number: int) -> dict[str, Any]:
	payload = fetch(f"{SCRIPTURES_BASE}/book/{book_id}/{chapter_number}/{verse_number}", fatal=False)
	return payload if isinstance(payload, dict) else {}

def enrich_chapter_with_verses(chapter_detail: dict[str, Any]) -> dict[str, Any]:
	book = chapter_detail.get("book") if isinstance(chapter_detail, dict) else None
	chapter = chapter_detail.get("chapter") if isinstance(chapter_detail, dict) else None
	book_id = book.get("_id") if isinstance(book, dict) else None
	chapter_number = chapter.get("number") if isinstance(chapter, dict) else None
	verses = chapter.get("verses") if isinstance(chapter, dict) else None

	if not book_id or not isinstance(chapter_number, int) or not isinstance(verses, list):
		return chapter_detail

	enriched_verses: list[dict[str, Any]] = []
	for index, verse in enumerate(verses, start=1):
		verse_detail = fetch_verse_detail(book_id, chapter_number, index)
		enriched_verse = dict(verse) if isinstance(verse, dict) else {"text": verse}
		enriched_verse["verseNumber"] = index
		enriched_verse["crossReferences"] = verse_detail.get("crossReferences", [])
		enriched_verse["jstReferences"] = verse_detail.get("jstReferences", [])
		enriched_verse["reference"] = verse_detail.get("reference")
		enriched_verse["book"] = verse_detail.get("book")
		enriched_verse["chapter"] = verse_detail.get("chapter")
		enriched_verse["verse"] = verse_detail.get("verse")
		enriched_verses.append(enriched_verse)

	updated_chapter = dict(chapter_detail)
	updated_chapter["chapter"] = dict(chapter)
	updated_chapter["chapter"]["verses"] = enriched_verses
	return updated_chapter

def chapter_needs_enrichment(chapter_detail: dict[str, Any]) -> bool:
	chapter = chapter_detail.get("chapter") if isinstance(chapter_detail, dict) else None
	verses = chapter.get("verses") if isinstance(chapter, dict) else None
	if not isinstance(verses, list):
		return False
	for verse in verses:
		if not isinstance(verse, dict):
			continue
		return "crossReferences" not in verse and "jstReferences" not in verse
	return False

def scrape_scriptures(output_dir: Path, enrich_verses: bool = False) -> dict[str, int]:
	stats = {"volumes": 0, "books": 0, "chapters": 0}
	root_dir = output_dir / "scriptures"
	ensure_dir(root_dir)

	vols_path = root_dir / "volumes.json"
	volumes_payload, volumes_cached = fetch_or_load_json(f"{SCRIPTURES_BASE}/volumes", vols_path)

	volumes = volumes_payload.get("volumes", []) if isinstance(volumes_payload, dict) else []
	for volume in volumes:
		volume_id = volume.get("_id")
		if not volume_id:
			continue

		stats["volumes"] += 1
		volume_folder = root_dir / volume_id
		ensure_dir(volume_folder)
		volume_path = volume_folder / "volume.json"
		volume_detail, volume_cached = fetch_or_load_json(f"{SCRIPTURES_BASE}/volume/{volume_id}", volume_path)

		books = volume_detail.get("books", []) if isinstance(volume_detail, dict) else []
		if not isinstance(books, list):
			books = []

		for book in books:
			book_id = book.get("_id")
			if not book_id:
				continue

			stats["books"] += 1
			book_folder = volume_folder / book_id
			ensure_dir(book_folder)
			book_path = book_folder / "book.json"
			book_detail, book_cached = fetch_or_load_json(f"{SCRIPTURES_BASE}/book/{book_id}", book_path)

			chapters = book_detail.get("chapters", []) if isinstance(book_detail, dict) else []
			if not isinstance(chapters, list):
				chapters = []
			chapter_folder = book_folder / chapter_folder_name(book_detail if isinstance(book_detail, dict) else {})
			ensure_dir(chapter_folder)

			for chapter in chapters:
				chapter_id = chapter.get("_id")
				if not chapter_id:
					continue

				stats["chapters"] += 1
				chap_path = chapter_folder / f"{chapter_id}.json"
				chapter_detail, chapter_cached = fetch_or_load_json(f"{SCRIPTURES_BASE}/chapter/{chapter_id}", chap_path)
				if enrich_verses and (not chapter_cached or chapter_needs_enrichment(chapter_detail if isinstance(chapter_detail, dict) else {})):
					# Only perform expensive per-verse enrichment when explicitly requested.
					chapter_detail = enrich_chapter_with_verses(chapter_detail if isinstance(chapter_detail, dict) else {})
					write_json(chap_path, chapter_detail)
					
	return stats

def resolve_output_dir(path: Path) -> Path:
	if path.is_absolute():
		return path.resolve()
	return (ROOT_DIR / path).resolve()

def fetch_paginated_entries(base_url: str, type_name: str, page_size: int = 500) -> tuple[dict[str, Any], int]:
	entries_dump: list[dict[str, Any]] = []
	page_count = 0
	total_entries = 0
	offset = 0
	while True:
		url = f"{base_url}/entries?type={type_name}&limit={page_size}&offset={offset}"
		payload = fetch(url)
		entries = payload.get("entries") if isinstance(payload, dict) else None
		if not isinstance(entries, list):
			break
		page_count += 1
		for entry in entries:
			if isinstance(entry, dict):
				entries_dump.append(entry)
		total = payload.get("total", 0) if isinstance(payload, dict) else 0
		if isinstance(total, int):
			total_entries = total
		offset += len(entries)
		if offset >= total or not entries:
			break
	return {"type": type_name, "total": total_entries or len(entries_dump), "entries": entries_dump}, page_count

def scrape_study_helps(output_dir: Path) -> dict[str, int]:
	stats = {"types": 0, "entries": 0}
	root_dir = output_dir / "study-helps"
	ensure_dir(root_dir)

	types_path = root_dir / "types.json"
	types_payload, types_cached = fetch_or_load_json(f"{STUDY_HELPS_BASE}/types", types_path)

	types = types_payload.get("types", []) if isinstance(types_payload, dict) else []
	for type_item in types:
		type_name = type_item.get("type")
		if not type_name:
			continue

		stats["types"] += 1
		type_dir = root_dir / slugify(type_name)
		ensure_dir(type_dir)

		entries_dump_path = type_dir / "entries.json"
		expected_entries = type_item.get("entryCount") if isinstance(type_item, dict) else None
		cached_entries_dump, entries_cached = fetch_or_load_json(
			f"{STUDY_HELPS_BASE}/entries?type={type_name}",
			entries_dump_path,
		)
		entries_dump: list[dict[str, Any]] = []
		entries_payload: dict[str, Any] | None = None
		needs_refresh = True
		if isinstance(cached_entries_dump, list):
			entries_dump = [entry for entry in cached_entries_dump if isinstance(entry, dict)]
			needs_refresh = not isinstance(expected_entries, int) or len(entries_dump) < expected_entries
		elif isinstance(cached_entries_dump, dict):
			entries_payload = cached_entries_dump
			entries_dump = [entry for entry in cached_entries_dump.get("entries", []) if isinstance(entry, dict)]
			total_entries = cached_entries_dump.get("total") if isinstance(cached_entries_dump.get("total"), int) else None
			needs_refresh = (
				not isinstance(expected_entries, int)
				or len(entries_dump) < expected_entries
				or (isinstance(total_entries, int) and len(entries_dump) < total_entries)
			)

		if needs_refresh:
			entries_payload, page_count = fetch_paginated_entries(STUDY_HELPS_BASE, type_name)
			entries_dump = [entry for entry in entries_payload.get("entries", []) if isinstance(entry, dict)]
			write_json(entries_dump_path, entries_payload)
			
		for entry in entries_dump:
			entry_id = entry.get("_id") or entry.get("entryId")
			if not entry_id:
				continue

			stats["entries"] += 1
			entry_path = type_dir / "entries" / f"{slugify(entry_id)}.json"
			fetch_or_load_json(f"{STUDY_HELPS_BASE}/entry/{entry_id}", entry_path)

	return stats

def main(argv: list[str] | None = None) -> int:
	parser = argparse.ArgumentParser(description="Scrape the Open Scripture API into JSON files")
	parser.add_argument(
		"--output",
		type=Path,
		default=DEFAULT_OUTPUT_DIR,
		help="directory where the dump will be written (relative to repo root unless absolute)",
	)
	parser.add_argument("--no-scriptures", action="store_true", help="skip scripture volumes/books/chapters")
	parser.add_argument("--no-study-helps", action="store_true", help="skip study help types/entries")
	parser.add_argument("--enrich-verses", action="store_true", help="enable per-verse enrichment (extra API calls)")
	args = parser.parse_args(argv)

	output_dir = resolve_output_dir(args.output)
	ensure_dir(output_dir)
	manifest: dict[str, Any] = {
		"scriptures": {},
		"studyHelps": {},
		"source": {
			"scripturesBase": SCRIPTURES_BASE,
			"studyHelpsBase": STUDY_HELPS_BASE,
		},
	}

	if not args.no_scriptures:
		manifest["scriptures"] = scrape_scriptures(output_dir, enrich_verses=bool(args.enrich_verses))

	if not args.no_study_helps:
		manifest["studyHelps"] = scrape_study_helps(output_dir)

	manifest_path = output_dir / "manifest.json"
	write_json(manifest_path, manifest)
	
	print("Download Complete!")
	print(json.dumps(manifest, indent=2))
	return 0

if __name__ == "__main__":
	raise SystemExit(main())
