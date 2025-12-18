import glob
import os
import sys
import dropbox

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python upload_dropbox.py videos_dir")

    token = os.getenv("DROPBOX_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("Missing DROPBOX_ACCESS_TOKEN secret")

    folder = os.getenv("DROPBOX_FOLDER") or "/TikTok/auto"
    videos_dir = sys.argv[1]

    dbx = dropbox.Dropbox(token)

    for fp in sorted(glob.glob(os.path.join(videos_dir, "*.mp4"))):
        name = os.path.basename(fp)
        dest = f"{folder}/{name}"

        with open(fp, "rb") as f:
            dbx.files_upload(f.read(), dest, mode=dropbox.files.WriteMode.overwrite)

        print(f"Uploaded {name} -> {dest}")

if __name__ == "__main__":
    main()
