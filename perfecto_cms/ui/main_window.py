import logging
import tkinter as tk
from dataclasses import dataclass

import customtkinter as ctk

from perfecto_cms.core.paths import BACKUP_DIR, DATA_FILE, IMAGE_DIR, PROJECT_ROOT
from perfecto_cms.ui.pages.base import PlaceholderPage
from perfecto_cms.ui.pages.combined_page import CombinedPage
from perfecto_cms.ui.pages.excel_page import ExcelPage
from perfecto_cms.ui.theme import COLORS, FONT_FAMILY, apply_theme


@dataclass(frozen=True)
class NavItem:
    key: str
    label: str
    description: str


NAV_ITEMS = [
    NavItem("catalog", "الكاتالوج", "إدارة الأقسام والمنتجات والأسعار."),
    NavItem("excel", "Excel", "استيراد وتصدير ملفات Excel."),
    NavItem("backups", "النسخ الاحتياطي", "عرض واسترجاع نسخ المنتجات الاحتياطية."),
    NavItem("settings", "الإعدادات", "إعدادات مسارات المشروع والتطبيق."),
    NavItem("about", "حول التطبيق", "معلومات عن تطبيق Perfecto CMS."),
]


class PerfectoCMSApp(ctk.CTk):
    def __init__(self):
        apply_theme()
        super().__init__()

        self.logger = logging.getLogger("perfecto_cms")
        self.title("Perfecto CMS - إدارة منيو برفكتو")
        self.geometry("1180x760")
        self.minsize(980, 640)
        self.configure(fg_color=COLORS["surface"])

        self.pages: dict[str, ctk.CTkFrame] = {}
        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        self.active_page = tk.StringVar(value=NAV_ITEMS[0].key)

        self._ensure_required_folders()
        self._build_layout()
        self._bind_shortcuts()
        self.show_page(NAV_ITEMS[0].key)
        self.logger.info("Main window initialized")

    def _ensure_required_folders(self) -> None:
        IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=260, fg_color=COLORS["red"], corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=18, pady=(22, 18))
        brand.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            brand,
            text="برفكتو",
            font=(FONT_FAMILY, 30, "bold"),
            text_color=COLORS["white"],
            anchor="e",
        ).grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            brand,
            text="Perfecto CMS",
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLORS["cream"],
            anchor="e",
        ).grid(row=1, column=0, sticky="ew", pady=(2, 0))

        nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav.grid(row=1, column=0, sticky="new", padx=14)
        nav.grid_columnconfigure(0, weight=1)

        for row, item in enumerate(NAV_ITEMS):
            button = ctk.CTkButton(
                nav,
                text=item.label,
                height=44,
                corner_radius=12,
                font=(FONT_FAMILY, 15, "bold"),
                fg_color="transparent",
                hover_color=COLORS["red_dark"],
                text_color=COLORS["white"],
                anchor="e",
                command=lambda key=item.key: self.show_page(key),
            )
            button.grid(row=row, column=0, sticky="ew", pady=4)
            self.nav_buttons[item.key] = button

        footer = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="sew", padx=18, pady=18)
        sidebar.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            footer,
            text=f"Project:\n{PROJECT_ROOT}",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["cream"],
            justify="right",
            anchor="e",
            wraplength=210,
        ).grid(row=0, column=0, sticky="ew")

        self.content = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        for item in NAV_ITEMS:
            if item.key == "catalog":
                page = CombinedPage(self.content)
            elif item.key == "excel":
                page = ExcelPage(self.content)
            else:
                page = PlaceholderPage(self.content, item.label, item.description)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[item.key] = page

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-s>", lambda _event: self._shortcut_not_ready("Save"))
        self.bind("<Control-n>", lambda _event: self._shortcut_not_ready("New Product"))
        self.bind("<Control-f>", lambda _event: self._shortcut_not_ready("Search"))
        self.bind("<Control-e>", lambda _event: self._shortcut_not_ready("Edit Product"))

    def _shortcut_not_ready(self, action: str) -> None:
        self.logger.info("Shortcut requested before feature is implemented: %s", action)

    def show_page(self, key: str) -> None:
        if key not in self.pages:
            self.logger.warning("Unknown page requested: %s", key)
            return

        self.active_page.set(key)
        page = self.pages[key]
        page.tkraise()

        refresh = getattr(page, "refresh", None)
        if callable(refresh):
            refresh()

        for item_key, button in self.nav_buttons.items():
            is_active = item_key == key
            button.configure(
                fg_color=COLORS["white"] if is_active else "transparent",
                text_color=COLORS["red"] if is_active else COLORS["white"],
                hover_color=COLORS["cream"] if is_active else COLORS["red_dark"],
            )
