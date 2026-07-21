import json
import os
from pathlib import Path
import re
import subprocess
import sys

# --- ANSI Colors ---
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
DIM = "\033[2m"


class KBCache:

    def __init__(self, cache_file="cache.json"):
        self.cache_file = Path(cache_file)
        self.data = self._load()

    def _load(self):
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text())
            except json.JSONDecodeError:
                return {}
        return {}

    def _save(self):
        self.cache_file.write_text(json.dumps(self.data, indent=2))

    def get(self, error_keyword):
        if error_keyword not in self.data:
            return None

        cached_entry = self.data[error_keyword]
        matching_files = cached_entry["files"]

        for file_path in matching_files:
            p = Path(file_path)
            if not p.exists():
                return None

            current_mtime = os.path.getmtime(p)
            if current_mtime > cached_entry["mtime"]:
                print(
                    f"{YELLOW}🔄 [Cache Stale] '{p.name}' was modified. Re-indexing...{RESET}"
                )
                return None

        return [Path(p) for p in matching_files]

    def set(self, error_keyword, file_paths):
        if not file_paths:
            return

        latest_mtime = max(os.path.getmtime(p) for p in file_paths)
        self.data[error_keyword] = {
            "files": [str(p) for p in file_paths],
            "mtime": latest_mtime,
        }
        self._save()


def parse_markdown_sections(md_text):
    """
    Splits markdown text into top-level blocks starting with '# '.
    This keeps '## What happened?' and '## How to fix it' grouped together under '# KeyError'!
    """
    # Split only on top-level H1 headers (# Header)
    raw_sections = re.split(r'\n(?=# )', md_text)
    return [sec.strip() for sec in raw_sections if sec.strip()]


def draw_ascii_box(title, text_content, border_color=CYAN):
    lines = text_content.strip().splitlines()
    max_len = max([len(line) for line in lines] + [len(title) + 4, 55])

    top_border = f"{border_color}┌── {BOLD}{title}{RESET}{border_color} {'─' * (max_len - len(title) - 5)}┐{RESET}"
    bottom_border = f"{border_color}└{'─' * (max_len - 1)}┘{RESET}"

    box = [top_border]
    for line in lines:
        padded = line + " " * (max_len - len(line) - 4)
        box.append(f"{border_color}│{RESET}  {padded}  {border_color}│{RESET}")
    box.append(bottom_border)

    return "\n".join(box)


def run_ripgrep_search(error_keyword, kb_path):
    rg_result = subprocess.run(
        ["rg", "-i", "-l", error_keyword, str(kb_path)],
        capture_output=True,
        text=True,
    )

    if not rg_result.stdout.strip():
        return []

    file_paths = [
        Path(p) for p in rg_result.stdout.strip().splitlines() if p.strip()
    ]

    def rank_key(path: Path):
        return 0 if error_keyword.lower() in path.stem.lower() else 1

    return sorted(file_paths, key=rank_key)


def run_and_troubleshoot(target_script, kb_folder_name):
    base_dir = Path(__file__).parent.resolve()
    kb_path = base_dir / kb_folder_name
    script_path = base_dir / target_script
    cache = KBCache(base_dir / "cache.json")

    # 1. Run target script
    result = subprocess.run(
        [sys.executable, str(script_path)], capture_output=True, text=True
    )

    if result.returncode == 0:
        print(result.stdout)
        return

    print(f"{BOLD}{RED}--- SCRIPT FAILED ---{RESET}")
    print(result.stderr)

    # 2. Extract error keyword
    stderr_lines = [
        line for line in result.stderr.splitlines() if line.strip()
    ]
    if not stderr_lines:
        return

    last_line = stderr_lines[-1]
    error_keyword = last_line.split(":")[0].strip()

    # 3. Check Cache
    matching_files = cache.get(error_keyword)

    if matching_files is not None:
        print(
            f"⚡ {GREEN}Cache Hit!{RESET} Instant lookup for: {BOLD}{YELLOW}'{error_keyword}'{RESET}\n"
        )
    else:
        print(
            f"🔍 {CYAN}Cache Miss! Searching KB with ripgrep:{RESET} {BOLD}{YELLOW}'{error_keyword}'{RESET}\n"
        )
        matching_files = run_ripgrep_search(error_keyword, kb_path)
        cache.set(error_keyword, matching_files)

    if not matching_files:
        print(f"{DIM}No matching documentation found in KB.{RESET}")
        return

    # 4. Render output with SECTION PARSING
    for idx, file_path in enumerate(matching_files):
        content = file_path.read_text()
        sections = parse_markdown_sections(content)

        # Filter only sections containing the error keyword
        relevant_sections = [
            sec for sec in sections if error_keyword.lower() in sec.lower()
        ]

        # If no specific section matched, fall back to displaying the whole file
        display_text = (
            "\n\n---\n\n".join(relevant_sections)
            if relevant_sections
            else content
        )

        is_top = idx == 0
        title = f"⭐ Top Match: {file_path.name}" if is_top else f"📄 Related: {file_path.name}"
        color = GREEN if is_top else CYAN

        print(draw_ascii_box(title, display_text, border_color=color))
        print()


if __name__ == "__main__":
    run_and_troubleshoot("error.py", "kb_test")
