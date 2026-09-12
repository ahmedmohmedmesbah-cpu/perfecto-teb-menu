import customtkinter as ctk
from tkinter import filedialog, messagebox
import shutil
import re
from pathlib import Path

from perfecto_cms.core.paths import IMAGE_DIR, PROJECT_ROOT
from perfecto_cms.core.data import DataManager
from perfecto_cms.ui.theme import COLORS, FONT_FAMILY


def generate_product_id(name: str) -> str:
    """Generate a product ID from the name."""
    # Convert Arabic to ASCII-friendly slug
    slug = re.sub(r'\s+', '-', name.strip())
    slug = re.sub(r'[^\w\-]', '', slug, flags=re.UNICODE)
    return slug.lower()


def project_relative_path(path: Path) -> str:
    """Return a website-friendly path relative to the project root."""
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


def unique_destination_path(source: Path) -> Path:
    """Create a non-conflicting destination under assets/images/products."""
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    destination = IMAGE_DIR / source.name

    if not destination.exists():
        return destination

    stem = source.stem
    suffix = source.suffix
    counter = 2

    while True:
        candidate = IMAGE_DIR / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


class ProductEditDialog(ctk.CTkToplevel):
    """Dialog for adding/editing products."""

    def __init__(self, parent, product=None, categories=None):
        super().__init__(parent)
        self.title("تحرير المنتج" if product else "إضافة منتج جديد")
        self.geometry("560x670")
        self.resizable(False, False)
        self.grab_set()

        self.product = product or {}
        self.categories = categories or []
        self.result = None
        self.image_path = self.product.get("image", "")

        self._build_form()

    def _build_form(self):
        """Build the product form."""
        frame = ctk.CTkFrame(self, fg_color=COLORS["surface"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(1, weight=1)

        # Product Name
        ctk.CTkLabel(
            frame,
            text="اسم المنتج *",
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
        if self.product:
            self.name_entry.insert(0, self.product.get("name", ""))

        # Price
        ctk.CTkLabel(
            frame,
            text="السعر *",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        ).grid(row=2, column=0, columnspan=2, sticky="e", pady=(0, 6))

        self.price_entry = ctk.CTkEntry(
            frame,
            font=(FONT_FAMILY, 13),
            fg_color=COLORS["white"],
            border_color=COLORS["beige"],
            border_width=1.5,
        )
        self.price_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        if self.product:
            self.price_entry.insert(0, str(self.product.get("price", "")))

        # Unit
        ctk.CTkLabel(
            frame,
            text="الوحدة *",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        ).grid(row=4, column=0, columnspan=2, sticky="e", pady=(0, 6))

        self.unit_entry = ctk.CTkEntry(
            frame,
            font=(FONT_FAMILY, 13),
            fg_color=COLORS["white"],
            border_color=COLORS["beige"],
            border_width=1.5,
        )
        self.unit_entry.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        if self.product:
            self.unit_entry.insert(0, self.product.get("unit", ""))

        # Category
        ctk.CTkLabel(
            frame,
            text="القسم *",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        ).grid(row=6, column=0, columnspan=2, sticky="e", pady=(0, 6))

        category_names = [cat.get("name", "") for cat in self.categories]
        category_ids = [cat.get("id", "") for cat in self.categories]

        self.category_var = ctk.StringVar(value=self.product.get("categoryId", "") if self.product else "")
        self.category_menu = ctk.CTkComboBox(
            frame,
            values=category_names,
            font=(FONT_FAMILY, 13),
            fg_color=COLORS["white"],
            border_color=COLORS["beige"],
            border_width=1.5,
            state="readonly",
            variable=self.category_var,
        )
        self.category_menu.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 14))

        self.category_ids = category_ids
        if self.product:
            category_id = self.product.get("categoryId", "")
            if category_id in category_ids:
                idx = category_ids.index(category_id)
                self.category_menu.set(category_names[idx] if idx < len(category_names) else "")

        # Product Image
        ctk.CTkLabel(
            frame,
            text="صورة المنتج",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        ).grid(row=8, column=0, columnspan=2, sticky="e", pady=(0, 6))

        image_frame = ctk.CTkFrame(frame, fg_color=COLORS["white"], corner_radius=10)
        image_frame.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        image_frame.grid_columnconfigure(0, weight=1)

        self.image_label = ctk.CTkLabel(
            image_frame,
            text=self._image_label_text(),
            font=(FONT_FAMILY, 12),
            text_color=COLORS["muted"],
            anchor="e",
        )
        self.image_label.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        image_buttons = ctk.CTkFrame(image_frame, fg_color="transparent")
        image_buttons.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

        ctk.CTkButton(
            image_buttons,
            text="إرفاق صورة",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["green"],
            hover_color="#2E6B2F",
            text_color=COLORS["white"],
            width=100,
            command=self._attach_photo,
        ).grid(row=0, column=0, padx=3)

        ctk.CTkButton(
            image_buttons,
            text="إزالة",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["beige"],
            hover_color="#C5B080",
            text_color=COLORS["text"],
            width=80,
            command=self._clear_photo,
        ).grid(row=0, column=1, padx=3)

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(20, 0))
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

    def _image_label_text(self):
        """Return the current image label text."""
        return self.image_path if self.image_path else "لا توجد صورة مرفقة"

    def _attach_photo(self):
        """Open a file picker and attach a product photo."""
        image_root = PROJECT_ROOT / "assets" / "images"
        selected = filedialog.askopenfilename(
            title="اختر صورة المنتج",
            initialdir=str(image_root if image_root.exists() else PROJECT_ROOT),
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.webp *.gif"),
                ("All Files", "*.*"),
            ],
        )

        if not selected:
            return

        source = Path(selected)

        try:
            self.image_path = project_relative_path(source)
        except ValueError:
            destination = unique_destination_path(source)
            shutil.copy2(source, destination)
            self.image_path = project_relative_path(destination)

        self.image_label.configure(text=self._image_label_text())

    def _clear_photo(self):
        """Remove the product photo link without deleting the image file."""
        self.image_path = ""
        self.image_label.configure(text=self._image_label_text())

    def _save(self):
        """Validate and save the product."""
        name = self.name_entry.get().strip()
        price_str = self.price_entry.get().strip()
        unit = self.unit_entry.get().strip()
        category_name = self.category_var.get().strip()

        # Validation
        if not name:
            messagebox.showerror("خطأ", "اسم المنتج مطلوب")
            return
        if not price_str:
            messagebox.showerror("خطأ", "السعر مطلوب")
            return
        if not unit:
            messagebox.showerror("خطأ", "الوحدة مطلوبة")
            return
        if not category_name:
            messagebox.showerror("خطأ", "القسم مطلوب")
            return

        try:
            price = float(price_str)
        except ValueError:
            messagebox.showerror("خطأ", "السعر يجب أن يكون رقم")
            return

        # Get category ID
        category_idx = -1
        for i, cat_name in enumerate([c.get("name", "") for c in self.categories]):
            if cat_name == category_name:
                category_idx = i
                break

        if category_idx < 0:
            messagebox.showerror("خطأ", "القسم غير صحيح")
            return

        # Generate or keep existing ID
        product_id = self.product.get("id") if self.product else generate_product_id(name)

        self.result = self.product.copy()
        self.result.update(
            {
                "id": product_id,
                "name": name,
                "price": price,
                "unit": unit,
                "categoryId": self.category_ids[category_idx],
                "image": self.image_path,
                "available": self.product.get("available", True),
            }
        )

        if "sellingPrice" in self.result:
            self.result["sellingPrice"] = price
        if "basePrice" not in self.result:
            self.result["basePrice"] = price

        self.destroy()


class ProductsPage(ctk.CTkFrame):
    """Page for managing products."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.data_manager = DataManager()
        self.categories = []
        self.products = []
        self.active_filter = "الكل"

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
            text="المنتجات",
            font=(FONT_FAMILY, 28, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 4))

        ctk.CTkLabel(
            header,
            text="إدارة المنتجات والأسعار والوحدات والصور.",
            font=(FONT_FAMILY, 15),
            text_color=COLORS["muted"],
            anchor="e",
        ).grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 18))

        # Filter and Action buttons
        button_frame = ctk.CTkFrame(header, fg_color="transparent")
        button_frame.grid(row=0, column=1, rowspan=2, sticky="ew", padx=22, pady=18)
        button_frame.grid_columnconfigure((0, 1, 2), weight=0)

        # Category filter
        ctk.CTkLabel(
            button_frame,
            text="فلتر:",
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=2, padx=(0, 8))

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
        self.filter_menu.grid(row=0, column=1, padx=(0, 16))

        ctk.CTkButton(
            button_frame,
            text="+ إضافة منتج",
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLORS["green"],
            hover_color="#2E6B2F",
            text_color=COLORS["white"],
            command=self._add_product,
        ).grid(row=0, column=3, padx=8)

        ctk.CTkButton(
            button_frame,
            text="تحديث",
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLORS["beige"],
            hover_color="#C5B080",
            text_color=COLORS["text"],
            command=self._load_data,
        ).grid(row=0, column=4, padx=8)

    def _build_content(self):
        """Build the main content area with scrollable product list."""
        content = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=16)
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # Scrollable frame for products
        self.scrollable_frame = ctk.CTkScrollableFrame(
            content,
            fg_color=COLORS["white"],
            corner_radius=16,
        )
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.product_items_frame = ctk.CTkFrame(
            self.scrollable_frame, fg_color="transparent"
        )
        self.product_items_frame.pack(fill="both", expand=True, padx=16, pady=16)
        self.product_items_frame.grid_columnconfigure(0, weight=1)

    def _load_data(self):
        """Load products and categories from JSON."""
        self.categories = self.data_manager.get_categories()
        self.products = self.data_manager.get_products()
        
        # Update filter menu with categories
        category_names = ["الكل"] + [cat.get("name", "") for cat in self.categories]
        self.filter_menu.configure(values=category_names)
        
        # Reset filter to "الكل"
        self.filter_var.set("الكل")
        self.active_filter = "الكل"
        
        self._render_products()

    def _on_filter_change(self, value=None):
        """Handle filter change."""
        self.active_filter = self.filter_var.get()
        self._render_products()

    def _render_products(self):
        """Render the list of products."""
        # Clear existing widgets
        for widget in self.product_items_frame.winfo_children():
            widget.destroy()

        # Filter products based on active filter
        filtered_products = self.products
        if self.active_filter != "الكل":
            # Find category ID by name
            category_id = None
            for cat in self.categories:
                if cat.get("name") == self.active_filter:
                    category_id = cat.get("id")
                    break
            
            if category_id:
                filtered_products = [p for p in self.products if p.get("categoryId") == category_id]

        if not filtered_products:
            ctk.CTkLabel(
                self.product_items_frame,
                text="لا توجد منتجات",
                font=(FONT_FAMILY, 16, "bold"),
                text_color=COLORS["muted"],
            ).pack(pady=40)
            return

        for idx, product in enumerate(filtered_products):
            self._create_product_card(idx, product)

    def _create_product_card(self, idx, product):
        """Create a product card."""
        border_color = COLORS["line"] if idx % 2 == 0 else None
        card = ctk.CTkFrame(
            self.product_items_frame,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_color=border_color,
            border_width=1 if border_color else 0,
        )
        card.pack(fill="x", pady=8)
        card.grid_columnconfigure(1, weight=1)

        # Product info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=12)
        info_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            info_frame,
            text=product.get("name", "N/A"),
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        ).grid(row=0, column=0, sticky="e")

        category = next(
            (cat for cat in self.categories if cat["id"] == product.get("categoryId")),
            None,
        )
        category_name = category.get("name", "N/A") if category else "N/A"

        info_text = (
            f"السعر: {product.get('price', 0)} جنيه | الوحدة: {product.get('unit', 'N/A')} | "
            f"القسم: {category_name}"
        )

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
            command=lambda p=product: self._edit_product(p),
        ).grid(row=0, column=0, padx=4)

        ctk.CTkButton(
            button_frame,
            text="حذف",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["red"],
            hover_color=COLORS["red_dark"],
            text_color=COLORS["white"],
            width=90,
            command=lambda pid=product.get("id"): self._delete_product(pid),
        ).grid(row=0, column=1, padx=4)

    def _add_product(self):
        """Open dialog to add a new product."""
        dialog = ProductEditDialog(self, product=None, categories=self.categories)
        self.wait_window(dialog)

        if dialog.result:
            if self.data_manager.add_product(dialog.result):
                messagebox.showinfo("نجح", "تم إضافة المنتج بنجاح")
                self._load_data()
            else:
                messagebox.showerror("خطأ", "فشل إضافة المنتج")

    def _edit_product(self, product):
        """Open dialog to edit a product."""
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
