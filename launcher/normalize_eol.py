"""Rewrite CRLF line endings to LF in the installed engine so the patches apply."""
import pathlib, sys

for f in pathlib.Path(sys.argv[1], "ios_homescreen").rglob("*"):
    if f.is_file() and f.suffix in (".py", ".js", ".html", ".css", ".json", ".svg", ".txt"):
        data = f.read_bytes()
        if b"\r\n" in data:
            f.write_bytes(data.replace(b"\r\n", b"\n"))
