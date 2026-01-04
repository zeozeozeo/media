import re
import subprocess
import sys
from pathlib import Path


def sh(*args):
    return subprocess.check_output(args, text=True).strip()


if len(sys.argv) != 3:
    print(f"Usage: python {sys.argv[0]} <start_commit> <end_commit>")
    print("Example: python script.py main feature-branch")
    sys.exit(1)

start_commit = sys.argv[1]
end_commit = sys.argv[2]

try:
    sh("git", "rev-parse", "--verify", start_commit)
    end_sha = sh("git", "rev-parse", "--verify", end_commit)
except subprocess.CalledProcessError:
    raise SystemExit(
        f"One or both commits '{start_commit}' or '{end_commit}' not found."
    )

files = [
    x
    for x in sh(
        "git",
        "diff",
        "--name-only",
        "--diff-filter=AM",
        f"{start_commit}..{end_commit}",
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
    raise SystemExit(
        f"No image files added/modified between {start_commit} and {end_commit}"
    )


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
