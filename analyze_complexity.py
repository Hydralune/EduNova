#!/usr/bin/env python3
"""Analyze cyclomatic complexity of Python source files in a project.

Usage:
  python analyze_complexity.py            # scan current directory
  python analyze_complexity.py path/to/dir

Requires:
  pip install radon

The script walks the given directory (recursively), finds all ``.py`` files (excluding
common virtual-env / node / git folders) and prints a table with:
  • File path
  • Number of blocks (functions / classes / methods)
  • Average CC score
  • Maximum (worst) CC score

At the end a project-level summary is shown.
"""
from __future__ import annotations

import os
import sys
from typing import List, Tuple

try:
    from radon.complexity import cc_visit, average_complexity
except ImportError:  # pragma: no cover – missing radon
    print("[!] This script depends on 'radon'. Install it via 'pip install radon' and rerun.")
    sys.exit(1)

IGNORED_DIRS = {'.git', '.hg', '.svn', '__pycache__', '.mypy_cache', '.venv', 'env', 'venv', 'node_modules', 'dist', 'build'}

# File extensions to include
LANG_EXTS = {
    'python': ['.py'],
    'typescript': ['.ts', '.tsx'],
    'javascript': ['.js', '.jsx'],
    'vue': ['.vue'],
}

# Thresholds based on radon: A<=5, B<=10, C<=20, D<=30, E<=40, F>40
COMPLEXITY_RATING = {
    "A": (0, 5),
    "B": (6, 10),
    "C": (11, 20),
    "D": (21, 30),
    "E": (31, 40),
    "F": (41, float('inf')),
}

def rate(score: float) -> str:
    """Return radon letter rating for a given score."""
    for letter, (lo, hi) in COMPLEXITY_RATING.items():
        if lo <= score <= hi:
            return letter
    return 'F'


def iter_source_files(base_path: str) -> List[str]:
    """Yield source file paths under *base_path* recursively, skipping IGNORED_DIRS."""
    files_out: List[str] = []
    exts_flat = {ext for exts in LANG_EXTS.values() for ext in exts}
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for filename in files:
            _, ext = os.path.splitext(filename)
            if ext in exts_flat:
                files_out.append(os.path.join(root, filename))
    return files_out


def analyze_file(path: str) -> Tuple[int, int, float, float]:
    """Return (lines, blocks, avg_cc, max_cc) for a single file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
    except (UnicodeDecodeError, FileNotFoundError):
        return 0, 0, 0.0, 0.0

    lines = source.count('\n') + 1
    blocks = cc_visit(source)
    if not blocks:
        return lines, 0, 0.0, 0.0
    avg = average_complexity(blocks)
    max_cc = max(b.complexity for b in blocks)
    return lines, len(blocks), avg, max_cc


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    if not os.path.isdir(target):
        print(f"[!] Provided path '{target}' is not a directory.")
        sys.exit(1)

    src_files = iter_source_files(target)
    if not src_files:
        print("No source files found.")
        return

    total_blocks = 0  # only Python
    total_lines = 0
    lines_per_lang = {lang: 0 for lang in LANG_EXTS.keys()}
    total_avg_sum = 0.0
    worst_score = 0.0
    worst_file = ''

    header = f"{'File':<60} {'Lines':>7} {'Blocks':>6} {'Avg CC':>8} {'Max CC':>8}"
    print(header)
    print('-' * len(header))

    for path in src_files:
        _, ext = os.path.splitext(path)
        # Determine language
        lang = next((l for l, exts in LANG_EXTS.items() if ext in exts), 'other')

        if ext == '.py':
            lines, blocks, avg, max_cc = analyze_file(path)
            total_blocks += blocks
            total_avg_sum += avg * blocks
            if max_cc > worst_score:
                worst_score = max_cc
                worst_file = path
        else:
            # Only count lines for non-python files
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.read().count('\n') + 1
            except Exception:
                lines = 0
            blocks = 0
            avg = max_cc = 0.0

        total_lines += lines
        lines_per_lang[lang] = lines_per_lang.get(lang, 0) + lines

        if lines == 0 and blocks == 0:
            continue
        print(f"{path[-60:]:<60} {lines:7d} {blocks:6d} {avg:8.2f} {max_cc:8.2f}  ({rate(avg) if blocks else '-'})")

    overall_avg = total_avg_sum / total_blocks if total_blocks else 0.0

    print('\nProject summary:')
    print(f"  Source files analyzed : {len(src_files)}")
    print(f"  Total code blocks (Python) : {total_blocks}")
    print(f"  Total lines of code        : {total_lines}")
    for lang, lines in lines_per_lang.items():
        if lines:
            print(f"    - {lang:<10}: {lines}")
    print(f"  Average complexity    : {overall_avg:.2f} ({rate(overall_avg)})")
    if worst_file:
        print(f"  Highest score         : {worst_score:.2f} in {worst_file}")

if __name__ == '__main__':
    main() 