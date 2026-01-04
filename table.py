import re
import subprocess
import sys
from pathlib import Path


def sh(*args, **kwargs):
    return subprocess.check_output(args, text=True, **kwargs).strip()


if len(sys.argv) != 3:
    print(f"Usage: python {sys.argv[0]} <start_commit> <end_commit>")
    sys.exit(1)

start_commit = sys.argv[1]
end_commit = sys.argv[2]

try:
    end_sha = sh("git", "rev-parse", end_commit)
    baseline = sh("git", "rev-parse", f"{start_commit}~1", stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    baseline = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

files = [
    x
    for x in sh(
        "git", "diff", "--name-only", "--diff-filter=AM", f"{baseline}..{end_sha}"
    ).splitlines()
    if x.strip()
]

remote = sh("git", "config", "--get", "remote.origin.url")
m = re.match(r"^git@github\.com:([^/]+)/(.+?)(?:\.git)?$", remote) or re.match(
    r"^https?://github\.com/([^/]+)/(.+?)(?:\.git)?/?$", remote
)
if not m:
    raise SystemExit("remote.origin.url is not a supported GitHub URL")

owner, repo = m.group(1), m.group(2)

img_exts = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
items = []

for f in files:
    p = Path(f)
    if p.suffix.lower() in img_exts:
        stem = re.sub(r"_[A-Za-z0-9]{6,}$", "", p.stem)
        title = re.sub(r"[_-]+", " ", stem).strip() or stem
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{end_sha}/{f}"
        items.append([title, raw_url, None])

cols = 3
if not items:
    print(f"No image files found between {start_commit} and {end_commit}")
    sys.exit(0)


def chunk(xs, n):
    return [xs[i : i + n] for i in range(0, len(xs), n)]


blocks = chunk(items, cols)

print(f"Found {len(items)} images. Please provide links:")
for bi, b in enumerate(blocks, 1):
    for ii, it in enumerate(b, 1):
        t = it[0]
        u = input(f'Link URL for "{t}" ({bi}.{ii}): ').strip()
        it[2] = u or "TODO"


def img_cell(t, u):
    return f"![{t}]({u})"


def link_cell(t, u):
    return f"[{t}]({u})"


first = blocks[0] + [["", "", ""]] * (cols - len(blocks[0]))
print(
    "\n" + "| " + " | ".join(img_cell(t, u) if t else "" for (t, u, _) in first) + " |"
)
print("|" + "|".join(["---"] * cols) + "|")
print("| " + " | ".join(link_cell(t, lu) if t else "" for (t, _, lu) in first) + " |")

for b in blocks[1:]:
    b = b + [["", "", ""]] * (cols - len(b))
    print("| " + " | ".join(img_cell(t, u) if t else "" for (t, u, _) in b) + " |")
    print("| " + " | ".join(link_cell(t, lu) if t else "" for (t, _, lu) in b) + " |")
