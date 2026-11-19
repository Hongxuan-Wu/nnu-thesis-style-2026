#!/usr/bin/env python3
"""Check the Skill package and source coverage; this does not inspect a thesis."""

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit


SKILL_NAME = "nnu-thesis-style-2026"


def parse_rules(text, page_count):
    rules = []
    identifiers = set()
    in_table = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip() == "| ID | 证据 | PDF页 | 规范或观察 |":
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            in_table = False
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if cells and all(re.fullmatch(r"[- :]+", cell) for cell in cells):
            continue
        if len(cells) != 4:
            raise ValueError("line {}: expected four rule columns".format(number))
        identifier, evidence, page_text, statement = cells
        if not re.fullmatch(r"[A-Z]+[0-9]{2}", identifier):
            raise ValueError("line {}: invalid rule ID".format(number))
        if identifier in identifiers:
            raise ValueError("duplicate rule ID: " + identifier)
        if evidence not in {"明确", "样例"}:
            raise ValueError(identifier + ": invalid evidence label")
        if not re.fullmatch(r"[0-9]+(?:,[0-9]+)*", page_text):
            raise ValueError(identifier + ": invalid source page list")
        pages = [int(page) for page in page_text.split(",")]
        if len(set(pages)) != len(pages) or any(
            page < 1 or page > page_count for page in pages
        ):
            raise ValueError(identifier + ": duplicate or out-of-range source page")
        if not statement:
            raise ValueError(identifier + ": empty statement")
        identifiers.add(identifier)
        rules.append({"id": identifier, "evidence": evidence, "pages": pages})
    if not rules:
        raise ValueError("no source rules found")
    covered = {page for rule in rules for page in rule["pages"]}
    missing = set(range(1, page_count + 1)) - covered
    if missing:
        raise ValueError("source pages not covered: " + str(sorted(missing)))
    return rules


def check_project(root):
    root = root.resolve()
    skill = root / "skills" / SKILL_NAME
    source = json.loads((skill / "references/source.json").read_text(encoding="utf-8"))
    if source["page_count"] != 17 or [p["number"] for p in source["pages"]] != list(range(1, 18)):
        raise ValueError("source manifest must index all 17 pages exactly once")
    if not re.fullmatch(r"[0-9a-f]{64}", source["sha256"]) or source["size_bytes"] <= 0:
        raise ValueError("invalid source identity")
    source_pdf = (skill / "references/source.pdf").read_bytes()
    if len(source_pdf) != source["size_bytes"]:
        raise ValueError("source PDF size mismatch")
    if hashlib.sha256(source_pdf).hexdigest() != source["sha256"]:
        raise ValueError("source PDF SHA256 mismatch")
    rules = parse_rules(
        (skill / "references/requirements.md").read_text(encoding="utf-8"),
        source["page_count"],
    )
    entry = (skill / "SKILL.md").read_text(encoding="utf-8")
    if not entry.startswith("---\n") or "\n---\n" not in entry[4:]:
        raise ValueError("missing Skill frontmatter")
    frontmatter = entry.split("---", 2)[1]
    if not re.search(r"^name: " + re.escape(SKILL_NAME) + r"$", frontmatter, re.M):
        raise ValueError("Skill name does not match its directory")
    if not re.search(r"^description: \S.+$", frontmatter, re.M):
        raise ValueError("missing Skill description")
    if source["sha256"] not in (skill / "references/source.md").read_text(encoding="utf-8"):
        raise ValueError("source digest differs between metadata and source note")
    ui = (skill / "agents/openai.yaml").read_text(encoding="utf-8")
    if "$" + SKILL_NAME not in ui:
        raise ValueError("UI default prompt must invoke the Skill")
    for path in root.rglob("*.md"):
        if ".git" in path.relative_to(root).parts:
            continue
        for destination in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            link = urlsplit(destination)
            if link.scheme or link.netloc or not link.path:
                continue
            target = (path.parent / unquote(link.path)).resolve()
            try:
                target.relative_to(root)
            except ValueError:
                raise ValueError("local reference escapes project: " + destination)
            if not target.exists():
                raise ValueError("broken local reference in {}: {}".format(path.name, destination))
    return {
        "rules": len(rules),
        "evidence": dict(Counter(rule["evidence"] for rule in rules)),
        "source_pages": source["page_count"],
        "coverage": "17/17",
        "source_pdf_sha256_verified": True,
        "thesis_file_checked": False,
    }


if __name__ == "__main__":
    try:
        result = check_project(Path(__file__).resolve().parents[1])
    except (ValueError, KeyError, OSError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        sys.exit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))
