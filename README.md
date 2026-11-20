# Rejig for Windows

Rearrange the real Home Screen on your iPhone from a Windows PC: pages, the dock, folders,
existing widgets, and which apps live only in the App Library. Nothing is installed on the
phone. Rejig lists every change before you apply it, saves a backup first, and reads the
phone back afterwards to check the result.

This is a Windows port of [Rejig](https://github.com/rejig-app/rejig) by keyclipse, which is
a Mac-only app. The engine, patches and MCP server are the same; the Mac window is replaced
by a small launcher that opens the editor in an Edge or Chrome app window.

## What it does

- Reads the Home Screen layout from your iPhone over USB (Wi-Fi after a one-time pairing).
- Drag apps, folders and existing widgets; add and remove pages; create folders; move apps
  to and from the App Library.
- Lists every change (moved, added, sent to the App Library) before you press **Apply**.
- Saves a layout backup before each write, then reads the phone again to confirm. If that
  check fails, it writes the backup back.
- Restores an earlier backup (**Backups**), and only ever writes to the iPhone a layout or
  backup came from.
- **Demo** mode lets you try everything on a pretend phone.
- Optional MCP server so an AI client (Claude Code, Codex, Claude Desktop) can read your
  Home Screen and propose an arrangement. Nothing is written until you click **Approve** in
  a Windows dialog.

## Requirements

- Windows 10 or 11
- [Python 3.12 or newer](https://www.python.org/downloads/windows/) with the `py` launcher
- [Git for Windows](https://git-scm.com/download/win)
- For a real phone: **Apple Devices** (Microsoft Store) or iTunes, which provide the USB
  driver. Without it only Demo mode works.
- An iPhone on iOS 17 or later for Wi-Fi mode

## Install

```powershell
git clone https://github.com/Mohaymen009/rejig-windows.git
cd rejig-windows
powershell -ExecutionPolicy Bypass -File install.ps1
```

This installs the engine and its patches into `%USERPROFILE%\Rejig` (dependencies are
pinned with hash checks) and adds a **Rejig** shortcut to your Desktop. It downloads about
120 Python packages, so it takes a few minutes.

## Use

1. Install Apple Devices from the Microsoft Store, plug in the iPhone, unlock it and tap
   **Trust This Computer**.
2. Double-click the **Rejig** shortcut (or run `%USERPROFILE%\Rejig\Rejig.cmd`).
3. Click **Read from phone**, rearrange, review **Changes**, then **Apply**.
4. Close the console window to stop Rejig.

Other modes:

```powershell
%USERPROFILE%\Rejig\Rejig.cmd --demo   # pretend phone, nothing real is touched
%USERPROFILE%\Rejig\Rejig.cmd --usb    # real phone over USB (default)
%USERPROFILE%\Rejig\Rejig.cmd --wifi   # after pairing over USB
```

Wi-Fi pairing: with the phone connected over USB and trusted, run
`%USERPROFILE%\Rejig\.venv\Scripts\python.exe -m ios_homescreen wifi setup`, then unplug and
use `--wifi`. The pairing is a `remote_<UDID>.plist` file in pymobiledevice3's folder
(`%USERPROFILE%\.pymobiledevice3` or `~/.local/share/pymobiledevice3`); treat it like a
password.

## Update

```powershell
git pull
powershell -ExecutionPolicy Bypass -File install.ps1
```

Your layouts, backups and pairing stay where they are.

## Connect an AI client (MCP)

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1 -RegisterMcp   # adds it to Claude Code
```

or add the server command yourself:
`%USERPROFILE%\Rejig\.venv\Scripts\python.exe -m rejig_mcp`.

Keep Rejig running with the phone connected, then ask your client to read your Home Screen.
Reading and drafting never touch the phone. Applying shows the exact numbered change list
in a Windows **Approve** dialog (or in the chat, where the client supports it); only your
click writes anything. Each write saves a backup first and reads the phone back. Nothing is
deleted or uninstalled.

The approval stops a model acting on its own; it is not a lock against other software
running as you on this PC.

## Your data

- Layouts and backups: `%USERPROFILE%\Rejig\data\`
- Cached icons: `%USERPROFILE%\Rejig\cache\`
- MCP plans: `%USERPROFILE%\Rejig\mcp\`
- Connection errors: `%USERPROFILE%\Rejig\backend.log`

Rejig sends nothing off your PC. The editor listens only on `127.0.0.1` with a fresh
session token. A layout backup is not a full iPhone backup.

## Uninstall

Removing Rejig changes nothing on your iPhone.

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\Rejig\.venv"      # keeps layouts and backups
Remove-Item -Recurse -Force "$env:USERPROFILE\Rejig"            # removes everything
Remove-Item "$([Environment]::GetFolderPath('Desktop'))\Rejig.lnk"
```

## Differences from the Mac version

- The window is an Edge/Chrome app window pointing at the local editor, not a native app.
- The MCP **Approve** window is a Windows dialog (`launcher/approve.py`).
- The MCP `select_connection` tool is not supported on Windows; restart Rejig with
  `--usb`, `--wifi` or `--demo` instead.
- The launcher cannot tell the MCP server about unsaved edits in the editor window, so
  apply or discard your own edits before asking an AI client to change things.
- The "Set Up Wi-Fi…" button does not exist; use the command above.
- Demo icons that are SVG are not converted to PNG for MCP clients (the Mac version uses
  `sips`), so they come back listed as missing.

## Tested on

- Windows 10 Pro, Python 3.12, iPhone 16 Pro Max on iOS 27.2.1 over USB: layout read,
  an approved MCP apply with backup and readback, and Demo mode.
- Not tested: Wi-Fi mode on Windows, Windows 11, restoring a backup on Windows, and the
  upstream unit tests under `tests/` (they were written for macOS).

Apple can change the private Home Screen service in any iOS release, so try Demo first and
keep the backup Rejig makes.

## Limits

These come from the engine and are the same as upstream: empty spaces made on the iPhone
itself close on the first Apply or Restore; Rejig moves existing widgets but cannot create
new ones. See the
[upstream README](https://github.com/rejig-app/rejig#limits) for details.

## Credits

- [Rejig](https://github.com/rejig-app/rejig) by keyclipse (MIT): the Mac app, MCP server
  and engine patches this is based on.
- [ios-homescreen](https://github.com/YakupEmreYerli/ios-homescreen) by Yakup Emre Yerli
  (MIT): reading and writing the layout, the editor and Demo mode.
- [pymobiledevice3](https://github.com/doronz88/pymobiledevice3) by doronz88 and
  contributors (GPL-3.0-or-later): talks to the iPhone.
- [srptools](https://github.com/idlesign/srptools) (BSD-3-Clause) and the
  [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) (MIT).

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). This project is not affiliated with or
endorsed by Apple, Rejig, ios-homescreen or pymobiledevice3. iPhone is a trademark of Apple
Inc.

## License

MIT. See [LICENSE](LICENSE).
