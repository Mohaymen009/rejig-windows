"""Windows Approve window for Rejig's MCP companion (stand-in for the Mac app's --approve).

Reads {"title": str, "lines": [str]} from stdin. Exit 0 = Approve, 1 = Decline, 2 = closed.
Escape declines; Return does nothing, so approving always takes a deliberate click.
"""
import json, sys, tkinter as tk
from tkinter import scrolledtext

try:
    body = json.loads(sys.stdin.read(1_000_001))
    title, lines = body["title"], body["lines"]
    assert isinstance(title, str) and title and len(title) <= 300
    assert isinstance(lines, list) and 0 < len(lines) <= 2000
    assert all(isinstance(x, str) and len(x) <= 400 and "\n" not in x for x in lines)
except Exception:
    sys.exit(2)

code = 2
root = tk.Tk()
root.title("Rejig: approve a Home Screen change")
root.geometry("640x460")
root.attributes("-topmost", True)
tk.Label(root, text=title, wraplength=600, justify="left", font=("Segoe UI", 10, "bold")).pack(padx=12, pady=8, anchor="w")
box = scrolledtext.ScrolledText(root, wrap="word", font=("Consolas", 10))
box.insert("1.0", "\n".join(lines))
box.configure(state="disabled")
box.pack(fill="both", expand=True, padx=12)


def finish(c):
    global code
    code = c
    root.destroy()


bar = tk.Frame(root)
bar.pack(pady=10)
tk.Button(bar, text="Decline", width=12, command=lambda: finish(1)).pack(side="left", padx=6)
tk.Button(bar, text="Approve", width=12, command=lambda: finish(0)).pack(side="left", padx=6)
root.bind("<Escape>", lambda e: finish(1))
root.protocol("WM_DELETE_WINDOW", lambda: finish(2))
root.after(600_000, lambda: finish(2))
root.mainloop()
sys.exit(code)
