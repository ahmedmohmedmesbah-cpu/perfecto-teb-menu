import customtkinter as ctk
from tkinter import messagebox
import re

from perfecto_cms.core.data import DataManager
from perfecto_cms.ui.theme import COLORS, FONT_FAMILY


CATEGORY_ICONS = {
    "apple": "تفاح",
    "milk": "لبن",
    "snow": "مجمد",
    "can": "معلبات",
    "sparkles": "براق",
    "basket": "سلة",
}


def generate_category_id(name: str) -> str:
    """Generate a category ID from the name."""
    slug = re.sub(r'\s+', '-', name.strip())
    slug = re.sub(r'[^\w\-]', '', slug, flags=re.UNICODE)
    return slug.lower()


class CategoryEditDialog(ctk.CTkToplevel):
    """Dialog for adding/editing categories."""

    def __init__(self, parent, category=None):
        super().__init__(parent)
        self.title("تحرير القسم" if category else "إضافة قسم جديد")
        self.geometry("400x350")
        self.resizable(False, False)
        self.grab_set()

        self.category = category or {}
        self.result = None

        self._build_form()

    def _build_form(self):
        """Build the category form."""
        frame = ctk.CTkFrame(self, fg_color=COLORS["surface"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(1, weight=1)

        # Category Name
        ctk.CTkLabel(
            frame,
            text="اسم القسم *",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        ).grid(row=0, column=0, columnspan=2, sticky="e", pady=(0, 6))

        self.name_entry = ctk.CTkEntry(
            frame,
            font=(FONT_FAMILY, 13),
            fg_color=COLORS["white"],
            border_color=COLORS["beige"],
            border_width=1.5,
        )
        self.name_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        if self.category:
            self.name_entry.insert(0, self.category.get("name", ""))

        # Icon
        ctk.CTkLabel(
            frame,
            text="الرمز *",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        ).grid(row=2, column=0, columnspan=2, sticky="e", pady=(0, 6))

        icon_names = list(CATEGORY_ICONS.values())
        icon_ids = list(CATEGORY_ICONS.keys())

        self.icon_var = ctk.StringVar(
            value=CATEGORY_ICONS.get(self.category.get("icon", ""), "")
        )
        self.icon_menu = ctk.CTkComboBox(
            frame,
            values=icon_names,
            font=(FONT_FAMILY, 13),
            fg_color=COLORS["white"],
            border_color=COLORS["beige"],
            border_width=1.5,
            state="readonly",
            variable=self.icon_var,
        )
        self.icon_menu.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 14))

        self.icon_ids = icon_ids
        if self.category:
            icon_id = self.category.get("icon", "")
            if icon_id in icon_ids:
                idx = icon_ids.index(icon_id)
                self.icon_menu.set(icon_names[idx] if idx < len(icon_names) else "")

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            button_frame,
            text="حفظ",
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLORS["green"],
            hover_color="#2E6B2F",
            text_color=COLORS["white"],
            command=self._save,
        ).grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ctk.CTkButton(
            button_frame,
            text="إلغاء",
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLORS["beige"],
            hover_color="#C5B080",
            text_color=COLORS["text"],
            command=self.destroy,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))

    def _save(self):
        """Validate and save the category."""
        name = self.name_entry.get().strip()
        icon_name = self.icon_var.get().strip()

        # Validation
        if not name:
            messagebox.showerror("خطأ", "اسم القسم مطلوب")
            return
        if not icon_name:
            messagebox.showerror("خطأ", "الرمز مطلوب")
            return

        # Get icon ID
        icon_idx = -1
        for i, iname in enumerate(CATEGORY_ICONS.values()):
            if iname == icon_name:
                icon_idx = i
                break

        if icon_idx < 0:
            messagebox.showerror("خطأ", "الرمز غير صحيح")
            return

        # Generate or keep existing ID
        category_id = self.category.get("id") if self.category else generate_category_id(name)

        self.result = {
            "id": category_id,
            "name": name,
            "icon": self.icon_ids[icon_idx],
        }

        self.destroy()


class CategoriesPage(ctk.CTkFrame):
    """Page for managing categories."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.data_manager = DataManager()
        self.categories = []

        self._build_header()
        self._build_content()
        self._load_data()

    def _build_header(self):
        """Build the page header."""
        header = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=16)
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 12))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="الأقسام",
            font=(FONT_FAMILY, 28, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 4))

        ctk.CTkLabel(
            header,
            text="إدارة أقسام المنيو وترتيبها.",
            font=(FONT_FAMILY, 15),
            text_color=COLORS["muted"],
            anchor="e",
        ).grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 18))

        # Action buttons
        button_frame = ctk.CTkFrame(header, fg_color="transparent")
        button_frame.grid(row=0, column=1, rowspan=2, sticky="ew", padx=22, pady=18)
        button_frame.grid_columnconfigure((0, 1), weight=0)

        ctk.CTkButton(
            button_frame,
            text="+ إضافة قسم",
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLORS["green"],
            hover_color="#2E6B2F",
            text_color=COLORS["white"],
            command=self._add_category,
        ).grid(row=0, column=0, padx=8)

        ctk.CTkButton(
            button_frame,
            text="تحديث",
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLORS["beige"],
            hover_color="#C5B080",
            text_color=COLORS["text"],
            command=self._load_data,
        ).grid(row=0, column=1, padx=8)

    def _build_content(self):
        """Build the main content area with scrollable category list."""
        content = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=16)
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # Scrollable frame for categories
        self.scrollable_frame = ctk.CTkScrollableFrame(
            content,
            fg_color=COLORS["white"],
            corner_radius=16,
        )
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.category_items_frame = ctk.CTkFrame(
            self.scrollable_frame, fg_color="transparent"
        )
        self.category_items_frame.pack(fill="both", expand=True, padx=16, pady=16)
        self.category_items_frame.grid_columnconfigure(0, weight=1)

    def _load_data(self):
        """Load categories from JSON."""
        self.categories = self.data_manager.get_categories()
        self._render_categories()

    def _render_categories(self):
        """Render the list of categories."""
        # Clear existing widgets
        for widget in self.category_items_frame.winfo_children():
            widget.destroy()

        if not self.categories:
            ctk.CTkLabel(
                self.category_items_frame,
                text="لا توجد أقسام",
                font=(FONT_FAMILY, 16, "bold"),
                text_color=COLORS["muted"],
            ).pack(pady=40)
            return

        for idx, category in enumerate(self.categories):
            self._create_category_card(idx, category)

    def _create_category_card(self, idx, category):
        """Create a category card."""
        card = ctk.CTkFrame(
            self.category_items_frame,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_color=COLORS["line"] if idx % 2 == 0 else None,
            border_width=1 if idx % 2 == 0 else 0,
        )
        card.pack(fill="x", pady=8)
        card.grid_columnconfigure(1, weight=1)

        # Category info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=12)
        info_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            info_frame,
            text=category.get("name", "N/A"),
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        ).grid(row=0, column=0, sticky="e")

        icon_name = CATEGORY_ICONS.get(category.get("icon", ""), "N/A")

        info_text = f"الرمز: {icon_name} | المعرّف: {category.get('id', 'N/A')}"

        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=(FONT_FAMILY, 12),
            text_color=COLORS["muted"],
            anchor="e",
        ).grid(row=1, column=0, sticky="e", pady=(4, 0))

        # Buttons
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.grid(row=0, column=2, sticky="ew", padx=16, pady=12)
        button_frame.grid_columnconfigure((0, 1), weight=0)

        ctk.CTkButton(
            button_frame,
            text="تحرير",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["beige"],
            hover_color="#C5B080",
            text_color=COLORS["text"],
            width=90,
            command=lambda c=category: self._edit_category(c),
        ).grid(row=0, column=0, padx=4)

        ctk.CTkButton(
            button_frame,
            text="حذف",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["red"],
            hover_color=COLORS["red_dark"],
            text_color=COLORS["white"],
            width=90,
            command=lambda cid=category.get("id"): self._delete_category(cid),
        ).grid(row=0, column=1, padx=4)

    def _add_category(self):
        """Open dialog to add a new category."""
        dialog = CategoryEditDialog(self, category=None)
        self.wait_window(dialog)

        if dialog.result:
            if self.data_manager.add_category(dialog.result):
                messagebox.showinfo("نجح", "تم إضافة القسم بنجاح")
                self._load_data()
            else:
                messagebox.showerror("خطأ", "فشل إضافة القسم")

    def _edit_category(self, category):
        """Open dialog to edit a category."""
        dialog = CategoryEditDialog(self, category=category)
        self.wait_window(dialog)

        if dialog.result:
            if self.data_manager.update_category(category["id"], dialog.result):
                messagebox.showinfo("نجح", "تم تحديث القسم بنجاح")
                self._load_data()
            else:
                messagebox.showerror("خطأ", "فشل تحديث القسم")

    def _delete_category(self, category_id):
        """Delete a category after confirmation."""
        if messagebox.askyesno("تأكيد", "هل تريد حذف هذا القسم؟"):
            if self.data_manager.delete_category(category_id):
                messagebox.showinfo("نجح", "تم حذف القسم بنجاح")
                self._load_data()
            else:
                messagebox.showerror("خطأ", "فشل حذف القسم")
