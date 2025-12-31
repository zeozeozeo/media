import subprocess
from pathlib import Path

opt_dir = Path("opt")
opt_dir.mkdir(exist_ok=True)

for p in Path(".").iterdir():
    if p.is_file() and p.suffix.lower() == ".png":
        out = opt_dir / p.name
        subprocess.run(
            ["pngquant", "--force", "--output", str(out), str(p)], check=True
        )
