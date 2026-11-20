"""Windows launcher for Rejig: starts the engine's local editor and opens it in an app window.

Usage: Rejig.cmd [--demo | --usb | --wifi]     (default: --usb)
"""
import json, os, re, subprocess, sys, shutil, webbrowser
from pathlib import Path

HOME = Path(os.environ.get("REJIG_SUPPORT_DIR") or Path.home() / "Rejig")
URL = re.compile(r"Open:\s*(http://127\.0\.0\.1:\d+/\?token=\S+)")


def open_window(url):
    for exe in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                shutil.which("msedge"), shutil.which("chrome")):
        if exe and Path(exe).exists():
            subprocess.Popen([exe, f"--app={url}"])
            return
    webbrowser.open(url)


def write_bridge(url, pid, connection):
    """Tell the MCP companion how to reach this editor (same file the Mac app writes)."""
    m = re.match(r"http://127\.0\.0\.1:(\d+)/\?token=(\S+)", url)
    tmp = HOME / ".mcp-bridge.json.tmp"
    tmp.write_text(json.dumps({"port": int(m.group(1)), "token": m.group(2), "pid": pid,
                               "connection": connection, "dirty": False}, sort_keys=True))
    os.replace(tmp, HOME / "mcp-bridge.json")


def main():
    mode = [a for a in sys.argv[1:] if a in ("--demo", "--wifi")]
    (HOME / "data").mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONUNBUFFERED="1", IOS_HOMESCREEN_CACHE_DIR=str(HOME / "cache"))
    log = open(HOME / "backend.log", "wb")
    proc = subprocess.Popen(
        [sys.executable, "-u", "-m", "ios_homescreen", "editor", "--no-browser",
         "--data-dir", str(HOME / "data"), *mode],
        stdout=subprocess.PIPE, stderr=log, env=env, text=True)
    try:
        opened = False
        for line in proc.stdout:
            print(line, end="")
            m = URL.search(line)
            if m and not opened:
                opened = True
                write_bridge(m.group(1), proc.pid, (mode or ["--usb"])[0].lstrip("-"))
                open_window(m.group(1))
                print("Rejig is running. Close this window or press Ctrl+C to stop it.")
        proc.wait()
    except KeyboardInterrupt:
        pass
    finally:
        if proc.poll() is None:
            proc.terminate()
        try:
            (HOME / "mcp-bridge.json").unlink()
        except OSError:
            pass


if __name__ == "__main__":
    main()
