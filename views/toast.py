import tkinter as tk

import config


class Toast:
    DURATION = 3000

    @classmethod
    def show(cls, root, message, color=config.OK):
        toast = tk.Toplevel(root)
        toast.withdraw()
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(bg=color)

        label = tk.Label(
            toast, text=message, bg=color, fg="white",
            font=(config.FONT_FAMILY, 10), padx=22, pady=12,
        )
        label.pack()

        toast.update_idletasks()
        w = toast.winfo_reqwidth()
        h = toast.winfo_reqheight()

        rx = root.winfo_rootx()
        ry = root.winfo_rooty()
        rw = root.winfo_width()
        rh = root.winfo_height()

        x = rx + rw - w - 20
        y = ry + rh - h - 50
        toast.geometry(f"{w}x{h}+{x}+{y}")
        toast.deiconify()

        toast.after(cls.DURATION, toast.destroy)
