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


def generate_product_id(name: str) -> str:
    """Generate a product ID from the name."""
    slug = re.sub(r'\s+', '-', name.strip())
    slug = re.sub(r'[^\w\-]', '', slug, flags=re.UNICODE)
    return slug.lower()


class CategorySelectionDialog(ctk.CTkToplevel):
    """Dialog for selecting a category from a list."""

    def __init__(self, parent, title, categories):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x250")
        self.resizable(False, False)
        self.grab_set()

        self.categories = categories
        self.result = None

        self._build_form(title)

    def _build_form(self, title):
        """Build the selection form."""
        frame = ctk.CTkFrame(self, fg_color=COLORS["surface"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            frame,
            text=title,
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="ew", pady=(0, 12))

        # Scrollable list of categories
        scroll_frame = ctk.CTkScrollableFrame(
            frame,
            fg_color=COLORS["white"],
            corner_radius=8,
        )
        scroll_frame.grid(row=1, column=0, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)

        for category in self.categories:
            cat_name = category.get("name", "")
            cat_id = category.get("id", "")

            btn = ctk.CTkButton(
                scroll_frame,
                text=cat_name,
                font=(FONT_FAMILY, 12),
                fg_color=COLORS["surface"],
                hover_color=COLORS["beige"],
                text_color=COLORS["text"],
                command=lambda cid=cat_id: self._select(cid),
            )
            btn.pack(fill="x", pady=4, padx=4)

        # Cancel button
        ctk.CTkButton(
            frame,
            text="إلغاء",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["beige"],
            hover_color="#C5B080",
            text_color=COLORS["text"],
            command=self.destroy,
        ).grid(row=2, column=0, sticky="ew", pady=(12, 0))

    def _select(self, category_id):
        """Select a category."""
        self.result = category_id
        self.destroy()


class CategoryEditDialog(ctk.CTkToplevel):
    """Dialog for editing a category with product management."""

    def __init__(self, parent, category, all_products, all_categories):
        super().__init__(parent)
        self.title("تحرير القسم")
        self.geometry("900x800")
        self.resizable(True, True)
        self.grab_set()

        self.category = category
        self.all_products = all_products
        self.all_categories = all_categories
        self.result = None
        self.product_checkboxes = {}

        self._build_form()

    def _build_form(self):
        """Build the category edit form with product management."""
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)

        # Category info section
        ctk.CTkLabel(
            main_frame,
            text="معلومات القسم",
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="e", pady=(0, 12))

        cat_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["white"], corner_radius=8)
        cat_frame.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        cat_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            cat_frame,
            text="اسم القسم",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="e", padx=12, pady=(12, 6))

        self.name_entry = ctk.CTkEntry(
            cat_frame,
            font=(FONT_FAMILY, 13),
            fg_color=COLORS["white"],
            border_color=COLORS["beige"],
            border_width=1.5,
            justify="right",
        )
        self.name_entry.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        self.name_entry.insert(0, self.category.get("name", ""))

        ctk.CTkButton(
            cat_frame,
            text="حفظ اسم القسم",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["green"],
            hover_color="#2E6B2F",
            text_color=COLORS["white"],
            command=self._save_category_name,
        ).grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))

        # Products section
        products_label_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        products_label_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        products_label_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            products_label_frame,
            text="المنتجات في هذا القسم",
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="e")

        category_id = self.category.get("id", "")
        category_products = [p for p in self.all_products if p.get("categoryId") == category_id]

        if category_products:
            select_frame = ctk.CTkFrame(products_label_frame, fg_color="transparent")
            select_frame.grid(row=0, column=1, sticky="e", padx=(0, 0))
            select_frame.grid_columnconfigure((0, 1), weight=0)

            ctk.CTkButton(
                select_frame,
                text="تحديد الكل",
                font=(FONT_FAMILY, 11, "bold"),
                fg_color=COLORS["beige"],
                hover_color="#C5B080",
                text_color=COLORS["text"],
                width=100,
                command=self._select_all,
            ).grid(row=0, column=0, padx=4)

            ctk.CTkButton(
                select_frame,
                text="إلغاء التحديد",
                font=(FONT_FAMILY, 11, "bold"),
                fg_color=COLORS["beige"],
                hover_color="#C5B080",
                text_color=COLORS["text"],
                width=100,
                command=self._deselect_all,
            ).grid(row=0, column=1, padx=4)

        # Scrollable products list
        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color=COLORS["white"], corner_radius=8)
        scroll_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 16))
        scroll_frame.grid_columnconfigure(0, weight=1)

        if not category_products:
            ctk.CTkLabel(
                scroll_frame,
                text="لا توجد منتجات في هذا القسم",
                font=(FONT_FAMILY, 12),
                text_color=COLORS["muted"],
            ).pack(pady=20)
        else:
            for product in category_products:
                product_id = product.get("id", "")
                product_name = product.get("name", "")

                item_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["surface"], corner_radius=8)
                item_frame.pack(fill="x", padx=8, pady=4)
                item_frame.grid_columnconfigure(1, weight=1)

                var = ctk.BooleanVar(value=False)
                self.product_checkboxes[product_id] = var

                ctk.CTkCheckBox(
                    item_frame,
                    text=product_name,
                    variable=var,
                    font=(FONT_FAMILY, 12),
                    text_color=COLORS["text"],
                ).grid(row=0, column=0, sticky="w", padx=8, pady=8)

                ctk.CTkLabel(
                    item_frame,
                    text=f"{product.get('price', 0)} جنيه",
                    font=(FONT_FAMILY, 11),
                    text_color=COLORS["muted"],
                ).grid(row=0, column=1, sticky="e", padx=8, pady=8)

        # Action buttons frame
        action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_frame.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        action_frame.grid_columnconfigure(0, weight=1)

        button_row1 = ctk.CTkFrame(action_frame, fg_color="transparent")
        button_row1.pack(fill="x", pady=(0, 8))
        button_row1.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            button_row1,
            text="🗑️ حذف المنتجات المختارة",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["red"],
            hover_color=COLORS["red_dark"],
            text_color=COLORS["white"],
            command=self._delete_selected_products,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        ctk.CTkButton(
            button_row1,
            text="➡️ نقل إلى قسم آخر",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["beige"],
            hover_color="#C5B080",
            text_color=COLORS["text"],
            command=self._move_to_category,
        ).grid(row=0, column=1, sticky="ew", padx=4)

        ctk.CTkButton(
            button_row1,
            text="➕ إضافة إلى قسم آخر",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["green"],
            hover_color="#2E6B2F",
            text_color=COLORS["white"],
            command=self._add_to_category,
        ).grid(row=0, column=2, sticky="ew", padx=(4, 0))

        button_row2 = ctk.CTkFrame(action_frame, fg_color="transparent")
        button_row2.pack(fill="x")
        button_row2.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            button_row2,
            text="إغلاق",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["beige"],
            hover_color="#C5B080",
            text_color=COLORS["text"],
            command=self.destroy,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

    def _save_category_name(self):
        """Save the category name and close the dialog."""
        new_name = self.name_entry.get().strip()

        if not new_name:
            messagebox.showerror("خطأ", "اسم القسم مطلوب")
            return

        category = self.category.copy()
        category["name"] = new_name
        self.result = {
            "action": "update_category",
            "category": category,
        }
        self.destroy()

    def _select_all(self):
        """Select all product checkboxes."""
        for var in self.product_checkboxes.values():
            var.set(True)

    def _deselect_all(self):
        """Deselect all product checkboxes."""
        for var in self.product_checkboxes.values():
            var.set(False)

    def _delete_selected_products(self):
        """Delete selected products."""
        selected_ids = [pid for pid, var in self.product_checkboxes.items() if var.get()]

        if not selected_ids:
            messagebox.showwarning("تحذير", "اختر منتجات لحذفها")
            return

        if not messagebox.askyesno("تأكيد", f"هل تريد حذف {len(selected_ids)} منتج(ات)؟"):
            return

        self.result = {
            "action": "delete_products",
            "product_ids": selected_ids,
        }

        self.destroy()

    def _move_to_category(self):
        """Move selected products to another category."""
        selected_ids = [pid for pid, var in self.product_checkboxes.items() if var.get()]

        if not selected_ids:
            messagebox.showwarning("تحذير", "اختر منتجات للنقل")
            return

        other_categories = [c for c in self.all_categories if c.get("id") != self.category.get("id")]
        if not other_categories:
            messagebox.showwarning("تحذير", "لا توجد أقسام أخرى للنقل إليها")
            return

        # Show category selection dialog
        cat_names = [c.get("name", "") for c in other_categories]
        cat_dialog = CategorySelectionDialog(self, "اختر القسم للنقل إليه", other_categories)
        self.wait_window(cat_dialog)

        if cat_dialog.result:
            self.result = {
                "action": "move_products",
                "product_ids": selected_ids,
                "new_category_id": cat_dialog.result,
            }
            self.destroy()

    def _add_to_category(self):
        """Add selected products to another category (duplicate)."""
        selected_ids = [pid for pid, var in self.product_checkboxes.items() if var.get()]

        if not selected_ids:
            messagebox.showwarning("تحذير", "اختر منتجات للإضافة")
            return

        other_categories = [c for c in self.all_categories if c.get("id") != self.category.get("id")]
        if not other_categories:
            messagebox.showwarning("تحذير", "لا توجد أقسام أخرى للإضافة إليها")
            return

        # Show category selection dialog
        cat_dialog = CategorySelectionDialog(self, "اختر القسم للإضافة إليه", other_categories)
        self.wait_window(cat_dialog)

        if cat_dialog.result:
            self.result = {
                "action": "add_to_category",
                "product_ids": selected_ids,
                "category_id": cat_dialog.result,
            }
            self.destroy()


class CombinedPage(ctk.CTkFrame):
    """Combined page for managing both products and categories."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.data_manager = DataManager()
        self.categories = []
        self.products = []
        self.active_filter = "الكل"
        self.expanded_categories = set()
        self.editing_category_id = None
        self.category_edit_entries = {}

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
            text="الأقسام والمنتجات",
            font=(FONT_FAMILY, 28, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 4))

        ctk.CTkLabel(
            header,
            text="إدارة الأقسام والمنتجات والأسعار.",
            font=(FONT_FAMILY, 15),
            text_color=COLORS["muted"],
            anchor="e",
        ).grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 18))

        # Buttons
        button_frame = ctk.CTkFrame(header, fg_color="transparent")
        button_frame.grid(row=0, column=1, rowspan=2, sticky="ew", padx=22, pady=18)
        button_frame.grid_columnconfigure((0, 1, 2, 3), weight=0)

        ctk.CTkLabel(
            button_frame,
            text="فلتر:",
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=3, padx=(0, 8))

        self.filter_var = ctk.StringVar(value="الكل")
        self.filter_menu = ctk.CTkComboBox(
            button_frame,
            values=["الكل"],
            font=(FONT_FAMILY, 12),
            fg_color=COLORS["white"],
            border_color=COLORS["beige"],
            border_width=1.5,
            state="readonly",
            variable=self.filter_var,
            command=self._on_filter_change,
        )
        self.filter_menu.grid(row=0, column=2, padx=(0, 16))

        ctk.CTkButton(
            button_frame,
            text="+ قسم",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["green"],
            hover_color="#2E6B2F",
            text_color=COLORS["white"],
            command=self._add_category,
        ).grid(row=0, column=1, padx=4)

        ctk.CTkButton(
            button_frame,
            text="+ منتج",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["green"],
            hover_color="#2E6B2F",
            text_color=COLORS["white"],
            command=self._add_product,
        ).grid(row=0, column=0, padx=4)

    def _build_content(self):
        """Build the main content area."""
        content = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=16)
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(
            content, fg_color=COLORS["white"], corner_radius=16
        )
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.items_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.items_frame.pack(fill="both", expand=True, padx=16, pady=16)
        self.items_frame.grid_columnconfigure(0, weight=1)

    def _load_data(self):
        """Load data from JSON."""
        self.categories = self.data_manager.get_categories()
        self.products = self.data_manager.get_products()

        category_names = ["الكل"] + [cat.get("name", "") for cat in self.categories]
        self.filter_menu.configure(values=category_names)

        self.filter_var.set("الكل")
        self.active_filter = "الكل"

        self._render_items()

    def refresh(self):
        """Refresh catalog data when the page is shown."""
        self._load_data()

    def _on_filter_change(self, value=None):
        """Handle filter change."""
        self.active_filter = self.filter_var.get()
        self._render_items()

    def _render_items(self):
        """Render categories and products."""
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        if not self.categories:
            ctk.CTkLabel(
                self.items_frame,
                text="لا توجد أقسام",
                font=(FONT_FAMILY, 16, "bold"),
                text_color=COLORS["muted"],
            ).pack(pady=40)
            return

        for category in self.categories:
            self._create_category_section(category)

    def _create_category_section(self, category):
        """Create a category section with its products."""
        category_id = category.get("id", "")
        category_name = category.get("name", "")

        # Filter products if needed
        if self.active_filter != "الكل":
            if self.active_filter != category_name:
                return

        cat_frame = ctk.CTkFrame(
            self.items_frame, fg_color=COLORS["surface"], corner_radius=12
        )
        cat_frame.pack(fill="x", pady=12)
        cat_frame.grid_columnconfigure(0, weight=1)

        # Category header
        header_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 8))
        header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_frame,
            text=category_name,
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLORS["red"],
        ).grid(row=0, column=0, sticky="e")

        cat_products = [p for p in self.products if p.get("categoryId") == category_id]
        count_text = f"({len(cat_products)} منتجات)"

        ctk.CTkLabel(
            header_frame,
            text=count_text,
            font=(FONT_FAMILY, 12),
            text_color=COLORS["muted"],
        ).grid(row=0, column=1, sticky="e", padx=8)

        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, sticky="e")
        button_frame.grid_columnconfigure((0, 1, 2), weight=0)

        is_expanded = category_id in self.expanded_categories or self.active_filter != "الكل"
        is_editing = category_id == self.editing_category_id

        ctk.CTkButton(
            button_frame,
            text="إغلاق" if is_expanded else "فتح",
            font=(FONT_FAMILY, 11, "bold"),
            fg_color=COLORS["green"],
            hover_color="#2E6B2F",
            text_color=COLORS["white"],
            width=70,
            command=lambda cid=category_id: self._toggle_category(cid),
        ).grid(row=0, column=0, padx=4)

        ctk.CTkButton(
            button_frame,
            text="إلغاء" if is_editing else "تحرير",
            font=(FONT_FAMILY, 11, "bold"),
            fg_color=COLORS["beige"],
            hover_color="#C5B080",
            text_color=COLORS["text"],
            width=80,
            command=lambda c=category: self._toggle_category_editor(c),
        ).grid(row=0, column=1, padx=4)

        ctk.CTkButton(
            button_frame,
            text="حذف",
            font=(FONT_FAMILY, 11, "bold"),
            fg_color=COLORS["red"],
            hover_color=COLORS["red_dark"],
            text_color=COLORS["white"],
            width=80,
            command=lambda cid=category_id: self._delete_category(cid),
        ).grid(row=0, column=2, padx=4)

        row_start = 1
        if is_editing:
            self._create_category_editor(cat_frame, category, row_start)
            row_start += 1

        # Products list
        if not is_expanded:
            return

        if not cat_products:
            ctk.CTkLabel(
                cat_frame,
                text="لا توجد منتجات في هذا القسم",
                font=(FONT_FAMILY, 12),
                text_color=COLORS["muted"],
            ).grid(row=row_start, column=0, sticky="ew", padx=12, pady=(0, 12))
            return

        for row, product in enumerate(cat_products, start=row_start):
            self._create_product_card(cat_frame, product, row)

    def _create_category_editor(self, parent, category, row):
        """Create an inline category editor inside the catalog page."""
        category_id = category.get("id", "")
        editor = ctk.CTkFrame(parent, fg_color=COLORS["white"], corner_radius=10)
        editor.grid(row=row, column=0, sticky="ew", padx=12, pady=(0, 8))
        editor.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            editor,
            text="تعديل اسم القسم",
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="e", padx=12, pady=(10, 4))

        name_entry = ctk.CTkEntry(
            editor,
            font=(FONT_FAMILY, 13),
            fg_color=COLORS["white"],
            border_color=COLORS["beige"],
            border_width=1.5,
            justify="right",
        )
        name_entry.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))
        name_entry.insert(0, category.get("name", ""))

        actions = ctk.CTkFrame(editor, fg_color="transparent")
        actions.grid(row=1, column=1, sticky="ew", padx=12, pady=(0, 10))

        ctk.CTkButton(
            actions,
            text="حفظ",
            font=(FONT_FAMILY, 11, "bold"),
            fg_color=COLORS["green"],
            hover_color="#2E6B2F",
            text_color=COLORS["white"],
            width=70,
            command=lambda cid=category_id: self._save_inline_category(cid),
        ).grid(row=0, column=0, padx=3)

        ctk.CTkButton(
            actions,
            text="إلغاء",
            font=(FONT_FAMILY, 11, "bold"),
            fg_color=COLORS["beige"],
            hover_color="#C5B080",
            text_color=COLORS["text"],
            width=70,
            command=self._cancel_inline_category,
        ).grid(row=0, column=1, padx=3)

        self.category_edit_entries[category_id] = name_entry

    def _toggle_category(self, category_id):
        """Open or close a category product list."""
        if category_id in self.expanded_categories:
            self.expanded_categories.remove(category_id)
        else:
            self.expanded_categories.add(category_id)
        self._render_items()

    def _toggle_category_editor(self, category):
        """Show or hide the inline category editor."""
        category_id = category.get("id")
        self.editing_category_id = (
            None if self.editing_category_id == category_id else category_id
        )
        if self.editing_category_id:
            self.expanded_categories.add(category_id)
        self._render_items()

    def _save_inline_category(self, category_id):
        """Save the inline category name editor."""
        entry = self.category_edit_entries.get(category_id)
        new_name = entry.get().strip() if entry else ""

        if not new_name:
            messagebox.showerror("خطأ", "اسم القسم مطلوب")
            return

        category = next((item for item in self.categories if item.get("id") == category_id), None)
        if not category:
            messagebox.showerror("خطأ", "لم يتم العثور على القسم")
            return

        updated_category = category.copy()
        updated_category["name"] = new_name

        if self.data_manager.update_category(category_id, updated_category):
            messagebox.showinfo("نجح", "تم تحديث القسم بنجاح")
            self.editing_category_id = None
            self._load_data()
        else:
            messagebox.showerror("خطأ", "فشل تحديث القسم")

    def _cancel_inline_category(self):
        """Close the inline category editor."""
        self.editing_category_id = None
        self._render_items()

    def _create_product_card(self, parent, product, start_row):
        """Create a product card within a category."""
        prod_frame = ctk.CTkFrame(parent, fg_color=COLORS["white"], corner_radius=8)
        prod_frame.grid(row=start_row, column=0, sticky="ew", padx=12, pady=4)
        prod_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            prod_frame,
            text=product.get("name", ""),
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="e", padx=8, pady=8)

        info_text = f"السعر: {product.get('price', 0)} | الوحدة: {product.get('unit', '')}"
        ctk.CTkLabel(
            prod_frame,
            text=info_text,
            font=(FONT_FAMILY, 11),
            text_color=COLORS["muted"],
        ).grid(row=0, column=1, sticky="e", padx=8, pady=8)

        button_frame = ctk.CTkFrame(prod_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, sticky="ew", padx=8, pady=8)
        button_frame.grid_columnconfigure((0, 1, 2, 3), weight=0)

        ctk.CTkButton(
            button_frame,
            text="تعديل",
            font=(FONT_FAMILY, 10, "bold"),
            fg_color=COLORS["beige"],
            hover_color="#C5B080",
            text_color=COLORS["text"],
            width=70,
            command=lambda p=product: self._edit_product(p),
        ).grid(row=0, column=0, padx=2)

        ctk.CTkButton(
            button_frame,
            text="نقل",
            font=(FONT_FAMILY, 10, "bold"),
            fg_color=COLORS["green"],
            hover_color="#2E6B2F",
            text_color=COLORS["white"],
            width=70,
            command=lambda p=product: self._move_one_product(p),
        ).grid(row=0, column=1, padx=2)

        ctk.CTkButton(
            button_frame,
            text="إضافة",
            font=(FONT_FAMILY, 10, "bold"),
            fg_color=COLORS["beige"],
            hover_color="#C5B080",
            text_color=COLORS["text"],
            width=70,
            command=lambda p=product: self._copy_one_product(p),
        ).grid(row=0, column=2, padx=2)

        ctk.CTkButton(
            button_frame,
            text="حذف",
            font=(FONT_FAMILY, 10, "bold"),
            fg_color=COLORS["red"],
            hover_color=COLORS["red_dark"],
            text_color=COLORS["white"],
            width=70,
            command=lambda pid=product.get("id"): self._delete_product(pid),
        ).grid(row=0, column=3, padx=2)

    def _add_category(self):
        """Add a new category."""
        from perfecto_cms.ui.pages.categories_page import CategoryEditDialog
        dialog = CategoryEditDialog(self, category=None)
        self.wait_window(dialog)

        if dialog.result:
            if self.data_manager.add_category(dialog.result):
                messagebox.showinfo("نجح", "تم إضافة القسم بنجاح")
                self._load_data()
            else:
                messagebox.showerror("خطأ", "فشل إضافة القسم")

    def _edit_category(self, category):
        """Edit a category with product management."""
        dialog = CategoryEditDialog(self, category, self.products, self.categories)
        self.wait_window(dialog)

        if dialog.result:
            action = dialog.result.get("action")

            if action == "delete_products":
                self._handle_delete_products(dialog.result.get("product_ids", []))
            elif action == "move_products":
                self._handle_move_products(
                    dialog.result.get("product_ids", []),
                    dialog.result.get("new_category_id"),
                )
            elif action == "add_to_category":
                self._handle_add_to_category(
                    dialog.result.get("product_ids", []),
                    dialog.result.get("category_id"),
                )
            elif action == "update_category":
                self._handle_update_category(
                    category.get("id"),
                    dialog.result.get("category", {}),
                )

            self._load_data()

    def _handle_update_category(self, category_id, category):
        """Update category details."""
        if self.data_manager.update_category(category_id, category):
            messagebox.showinfo("نجح", "تم تحديث القسم بنجاح")
        else:
            messagebox.showerror("خطأ", "فشل تحديث القسم")

    def _handle_delete_products(self, product_ids):
        """Delete products."""
        for pid in product_ids:
            self.data_manager.delete_product(pid)

    def _handle_move_products(self, product_ids, new_category_id):
        """Move products to another category."""
        for pid in product_ids:
            product = next((p for p in self.products if p["id"] == pid), None)
            if product:
                product["categoryId"] = new_category_id
                self.data_manager.update_product(pid, product)

    def _handle_add_to_category(self, product_ids, category_id):
        """Add products to another category (create copies)."""
        for pid in product_ids:
            product = next((p for p in self.products if p["id"] == pid), None)
            if product:
                new_product = product.copy()
                new_product["id"] = self._make_unique_product_id(product["id"], category_id)
                new_product["categoryId"] = category_id
                self.data_manager.add_product(new_product)

    def _make_unique_product_id(self, product_id, category_id):
        """Create a unique ID when copying a product into another category."""
        existing_ids = {str(product.get("id")) for product in self.data_manager.get_products()}
        base_id = f"{product_id}-{category_id}"
        new_id = base_id
        counter = 2

        while new_id in existing_ids:
            new_id = f"{base_id}-{counter}"
            counter += 1

        return new_id

    def _move_one_product(self, product):
        """Move one product to another category."""
        other_categories = [c for c in self.categories if c.get("id") != product.get("categoryId")]
        if not other_categories:
            messagebox.showwarning("تحذير", "لا توجد أقسام أخرى للنقل إليها")
            return

        dialog = CategorySelectionDialog(self, "اختر القسم للنقل إليه", other_categories)
        self.wait_window(dialog)

        if dialog.result:
            product_copy = product.copy()
            product_copy["categoryId"] = dialog.result
            if self.data_manager.update_product(product.get("id"), product_copy):
                messagebox.showinfo("نجح", "تم نقل المنتج بنجاح")
                self.expanded_categories.add(dialog.result)
                self._load_data()
            else:
                messagebox.showerror("خطأ", "فشل نقل المنتج")

    def _copy_one_product(self, product):
        """Copy one product to another category."""
        other_categories = [c for c in self.categories if c.get("id") != product.get("categoryId")]
        if not other_categories:
            messagebox.showwarning("تحذير", "لا توجد أقسام أخرى للإضافة إليها")
            return

        dialog = CategorySelectionDialog(self, "اختر القسم للإضافة إليه", other_categories)
        self.wait_window(dialog)

        if dialog.result:
            new_product = product.copy()
            new_product["id"] = self._make_unique_product_id(product.get("id"), dialog.result)
            new_product["categoryId"] = dialog.result
            if self.data_manager.add_product(new_product):
                messagebox.showinfo("نجح", "تم إضافة نسخة من المنتج للقسم الآخر")
                self.expanded_categories.add(dialog.result)
                self._load_data()
            else:
                messagebox.showerror("خطأ", "فشل إضافة المنتج للقسم الآخر")

    def _add_product(self):
        """Add a new product."""
        from perfecto_cms.ui.pages.products_page import ProductEditDialog
        dialog = ProductEditDialog(self, product=None, categories=self.categories)
        self.wait_window(dialog)

        if dialog.result:
            if self.data_manager.add_product(dialog.result):
                messagebox.showinfo("نجح", "تم إضافة المنتج بنجاح")
                self._load_data()
            else:
                messagebox.showerror("خطأ", "فشل إضافة المنتج")

    def _edit_product(self, product):
        """Edit a product."""
        from perfecto_cms.ui.pages.products_page import ProductEditDialog
        dialog = ProductEditDialog(self, product=product, categories=self.categories)
        self.wait_window(dialog)

        if dialog.result:
            if self.data_manager.update_product(product["id"], dialog.result):
                messagebox.showinfo("نجح", "تم تحديث المنتج بنجاح")
                self._load_data()
            else:
                messagebox.showerror("خطأ", "فشل تحديث المنتج")

    def _delete_product(self, product_id):
        """Delete a product after confirmation."""
        if messagebox.askyesno("تأكيد", "هل تريد حذف هذا المنتج؟"):
            if self.data_manager.delete_product(product_id):
                messagebox.showinfo("نجح", "تم حذف المنتج بنجاح")
                self._load_data()
            else:
                messagebox.showerror("خطأ", "فشل حذف المنتج")

    def _delete_category(self, category_id):
        """Delete a category after confirmation."""
        # Count products in this category
        cat_products = [p for p in self.products if p.get("categoryId") == category_id]

        if cat_products:
            msg = f"هذا القسم يحتوي على {len(cat_products)} منتج(ات). حذف القسم سيترك المنتجات بدون تصنيف.\nهل تريد المتابعة؟"
        else:
            msg = "هل تريد حذف هذا القسم؟"

        if messagebox.askyesno("تأكيد", msg):
            if self.data_manager.delete_category(category_id):
                messagebox.showinfo("نجح", "تم حذف القسم بنجاح")
                self._load_data()
            else:
                messagebox.showerror("خطأ", "فشل حذف القسم")
