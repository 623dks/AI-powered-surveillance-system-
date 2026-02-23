import argparse
import shutil
from pathlib import Path
import re

IMG_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

parser = argparse.ArgumentParser(description='Merge YOLO-format fire dataset into project train set and remap class ids')
parser.add_argument('--src', required=True, help='Path to extracted fire dataset root')
parser.add_argument('--images-dst', default='data/images/train', help='Destination images folder')
parser.add_argument('--labels-dst', default='data/labels/train', help='Destination labels folder')
parser.add_argument('--old-class', type=int, default=0, help='Class id used in fire dataset (usually 0)')
parser.add_argument('--new-class', type=int, default=5, help='Target class id in your dataset (e.g., 5)')
parser.add_argument('--prefix', default='fire_', help='Prefix to add to copied image filenames to avoid collisions')
args = parser.parse_args()

src = Path(args.src)
images_dst = Path(args.images_dst)
labels_dst = Path(args.labels_dst)
old_class = str(args.old_class)
new_class = str(args.new_class)
prefix = args.prefix

if not src.exists():
    print(f"Source path does not exist: {src}")
    raise SystemExit(1)

# Find candidate image and label folders inside src
candidates = []
for p in src.rglob('*'):
    if p.is_dir():
        # Candidate if contains images and labels subfolders
        imgs = list(p.rglob('*'))

# We'll scan for files with image extensions and corresponding .txt labels
images_dst.mkdir(parents=True, exist_ok=True)
labels_dst.mkdir(parents=True, exist_ok=True)

copied = 0
for img in src.rglob('*'):
    if img.suffix.lower() in IMG_EXTS:
        # Determine label filename
        rel = img.name
        label_name = img.with_suffix('.txt').name
        # Create unique destination name
        dst_name = prefix + img.name
        dst_img = images_dst / dst_name
        # Copy image
        shutil.copy2(img, dst_img)
        # Handle label if exists
        src_label = img.with_suffix('.txt')
        dst_label = labels_dst / (prefix + label_name)
        if src_label.exists():
            # Remap class ids in label file
            lines = src_label.read_text().splitlines()
            new_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if parts[0] == old_class:
                    parts[0] = new_class
                new_lines.append(' '.join(parts))
            dst_label.write_text('\n'.join(new_lines))
        else:
            # Create empty label file
            dst_label.write_text('')
        copied += 1

print(f"Done. Copied {copied} images to {images_dst} and labels to {labels_dst} (remapped class {old_class} -> {new_class})")
