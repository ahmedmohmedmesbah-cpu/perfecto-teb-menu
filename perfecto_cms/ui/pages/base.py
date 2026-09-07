import customtkinter as ctk

from perfecto_cms.ui.theme import COLORS, FONT_FAMILY


class PlaceholderPage(ctk.CTkFrame):
    def __init__(self, master, title: str, description: str):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=16)
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 12))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=title,
            font=(FONT_FAMILY, 28, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 4))

        ctk.CTkLabel(
            header,
            text=description,
            font=(FONT_FAMILY, 15),
            text_color=COLORS["muted"],
            anchor="e",
        ).grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 18))

        content = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=16)
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        content.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            content,
            text="سيتم تنفيذ هذا الجزء في المرحلة الخاصة به.",
            font=(FONT_FAMILY, 18, "bold"),
            text_color=COLORS["red"],
        ).grid(row=0, column=0, padx=24, pady=40)
