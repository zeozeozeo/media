import re
import subprocess
from pathlib import Path


def sh(*args):
    return subprocess.check_output(args, text=True).strip()


sha = sh("git", "rev-parse", "HEAD")
files = [
    x
    for x in sh(
        "git", "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "HEAD"
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
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{sha}/{f}"
        items.append([title, raw_url, None])

cols = 3
if not items:
    raise SystemExit("No image files found in latest commit")


def chunk(xs, n):
    return [xs[i : i + n] for i in range(0, len(xs), n)]


blocks = chunk(items, cols)

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
print("| " + " | ".join(img_cell(t, u) if t else "" for (t, u, _) in first) + " |")
print("|" + "|".join(["---"] * cols) + "|")
print("| " + " | ".join(link_cell(t, lu) if t else "" for (t, _, lu) in first) + " |")

for b in blocks[1:]:
    b = b + [["", "", ""]] * (cols - len(b))
    print("| " + " | ".join(img_cell(t, u) if t else "" for (t, u, _) in b) + " |")
    print("| " + " | ".join(link_cell(t, lu) if t else "" for (t, _, lu) in b) + " |")
