# The Scriptures

The **Standard** Works of the [Church of Jesus Christ of Latter-day Saints](https://www.churchofjesuschrist.org) are:

- The Authorized King James Version (KJV) of the Bible, consisting of the *Old Testament* and the *New Testament*
- *The Book of Mormon*, subtitled since 1981 "Another Testament of Jesus Christ"
- *The Doctrine and Covenants* (D&C)
- *The Pearl of Great Price* (containing the Book of Moses, the Book of Abraham, Joseph Smith–Matthew, Joseph Smith–History, and the Articles of Faith)


## Documentation

**What this repository contains**
- **Merged Scriptures:** JSON copies of the Standard Works and study helps. Full copies live in the `complete/` directory; flattened, per-chapter files are in `flat/`; images are under `images/`; and reference data is in `reference/`.
- **Scripts:** Small Python utilities live in `scripts/` for downloading source data, producing flattened files, and building references.
- **Scriptures:** The `scriptures/` folder contains the hierarchical per-volume/per-book structure.
- **Study helps:** The `helps/` folder contains JSON files for the various study helps (e.g. Bible Dictionary, Topical Guide, etc.)

**Running the scripts**
Prerequisites: Python 3.8+ is recommended.
```powershell
# Examples:
python scripts/download.py        # download or refresh source data
python scripts/make-flat.py       # produce flattened JSON files
python scripts/make-reference.py  # build reference JSON
python scripts/complete.py        # combine pieces into complete/scriptures.json
```

**Git LFS**
The complete scriptures are stored with Git LFS to keep the repository lightweight. To access the full data, install Git LFS and run:

```bash
# install Git LFS (OS-specific installer) then:
git lfs install
git lfs pull
```

**Sources and credits**
* https://www.churchofjesuschrist.org
* https://openscriptureapi.org
* https://github.com/bcbooks/scriptures-json
* https://scriptures.nephi.org
