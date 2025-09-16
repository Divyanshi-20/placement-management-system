# scan_templates.py
import re, os, sys
from pathlib import Path

project_root = Path(__file__).parent
templates_dir = project_root / "templates"

patterns = []
for p in Path(project_root / "enhancements").rglob("*.py"):
    txt = p.read_text(errors="ignore")
    for m in re.finditer(r"render_template\(\s*[\"']([^\"']+\.html)[\"']", txt):
        patterns.append((p.name, m.group(1)))

print("render_template usages and file existence:\n")
for src, tpl in patterns:
    tpl_path = templates_dir / tpl
    print(f"{src:25} -> {tpl:40}  exists: {tpl_path.exists()}")
