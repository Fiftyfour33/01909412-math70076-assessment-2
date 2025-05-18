#!/usr/bin/env python3
"""
Download the AP-NORC VoteCast Public-Use Files (PUFs) and the accompanying
code-books, verify their SHA-256 digests, and unzip them into data/raw/.

Usage
-----
$ python data/get_votecast.py          # interactive (downloads if needed)
$ python data/get_votecast.py --force  # re-download even if file exists
"""
import hashlib, os, sys, zipfile, urllib.request, argparse, textwrap
from pathlib import Path

FILES = [{"name": "VoteCast 2020 PUF",
          "url": "https://apnorc.org/wp-content/uploads/2021/05/AP-VoteCast-2020-Public-Use-Files.zip",
          "sha256": "430d3994d03d5e119d8be8359cf8de9f98a5f2f1e161ff15a1ebf59e1ce8b488"},
         {"name": "VoteCast 2024 PUF",
          "url": "https://apnorc.org/wp-content/uploads/2021/05/AP_VOTECAST_2024_GENERAL.zip",
          "sha256": "7d63dada53d1e6f5f3fac54417e189755d54ce312cf7945f16abe4f91c5bf62f"}]

DEST_DIR = Path("data/raw")
# download first, then move if hash OK
TMP_DIR = Path("data/tmp")
CHUNK_SIZE = 1 << 14 # 16 KiB

def sha256_of(path: Path) -> str:
    """Return hex sha-256 of a file (streamed)."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()

def fetch(url: str, dst: Path) -> None:
    """Download a file with a tiny progress bar."""
    from tqdm.auto import tqdm  # pip install tqdm
    with urllib.request.urlopen(url) as resp, dst.open("wb") as out:
        total = int(resp.getheader("Content-Length", 0))
        with tqdm(total=total, unit="B", unit_scale=True, desc=dst.name) as bar:
            while True:
                chunk = resp.read(CHUNK_SIZE)
                if not chunk:
                    break
                out.write(chunk)
                bar.update(len(chunk))

def unzip(zip_path: Path, dest_dir: Path) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest_dir)

def main(force: bool=False):
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    for meta in FILES:
        url, expected = meta["url"], meta["sha256"]
        filename = Path(url).name
        final_path = DEST_DIR / filename
        tmp_path = TMP_DIR / filename

        # Skip if already present & verified
        if final_path.exists() and not force:
            if expected != "":  # we know what to expect
                if sha256_of(final_path) == expected:
                    print(f"Source data {filename} already present & verified; no action needed.")
                    continue
                else:
                    print(f"Hash mismatch! Re-downloading {filename}.")
            else:
                print(f"Source data {filename} already present, yet no hash stored; use --force to re-download.")
                continue

        print(f"\nDownloading: {meta['name']}")
        fetch(url, tmp_path)

        # Verify
        digest = sha256_of(tmp_path)
        print(f"   SHA-256: {digest}")
        if expected and digest != expected:
            print("Hash mismatch! Aborting for safety.")
            tmp_path.unlink(missing_ok=True)
            continue

        # Move & unzip
        tmp_path.rename(final_path)
        if final_path.suffix == ".zip":
            print("   Unzipping...")
            unzip(final_path, DEST_DIR)
        print("   Done.\n")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Fetch AP-NORC VoteCast data and verify SHA-256 digests.")
    ap.add_argument("--force", action="store_true", help="re-download even if file exists")
    args = ap.parse_args()
    main(force=args.force)
