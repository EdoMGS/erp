import pathlib
import re
import sys


def fix_text(text: str) -> str:
    # normalize CRLF to LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    out_lines = []
    for line in text.splitlines(keepends=True):
        # replace tabs only in the leading indentation portion
        line = re.sub(r'^(?P<indent>[ \t]+)',
                      lambda m: m.group('indent').replace('\t', '    '),
                      line)
        # strip trailing spaces/tabs (before newline)
        line = re.sub(r'[ \t]+(?=\n$)', '', line)
        out_lines.append(line)
    fixed = ''.join(out_lines)
    # ensure final newline
    if not fixed.endswith("\n"):
        fixed += "\n"
    return fixed


def fix_file(path: pathlib.Path):
    txt = path.read_text(encoding="utf-8", errors="ignore")
    fixed = fix_text(txt)
    if fixed != txt:
        path.write_text(fixed, encoding="utf-8", newline="\n")
    print(f"fixed: {path}")


def main():
    paths = [pathlib.Path(p) for p in sys.argv[1:]] or []
    if not paths:
        print("usage: python scripts/fix_indent.py <file1.py> [file2.py ...]")
        sys.exit(2)
    for p in paths:
        if p.exists() and p.suffix == ".py":
            fix_file(p)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
