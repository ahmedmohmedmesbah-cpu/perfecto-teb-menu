import customtkinter as ctk


COLORS = {
    "red": "#AD263C",
    "red_dark": "#861B2C",
    "green": "#3E8E41",
    "cream": "#F3E8C5",
    "beige": "#D6C09A",
    "text": "#222222",
    "muted": "#6F6A62",
    "white": "#FFFFFF",
    "surface": "#FBFAF7",
    "line": "#EADFC9",
    "blue": "#4A90E2",
}

FONT_FAMILY = "Segoe UI"


def apply_theme() -> None:
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
