import customtkinter as ctk
from tkinter import messagebox, filedialog
import re
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

from perfecto_cms.core.data import DataManager
from perfecto_cms.ui.theme import COLORS, FONT_FAMILY


HEADER_ALIASES = {
    "code": {"item code", "code", "الكود", "كود"},
    "name": {"name", "product name", "الصنف", "اسم المنتج", "المنتج"},
    "price": {"price", "البيع", "السعر", "سعر"},
    "selling_price": {"selling price", "سعر الربع", "quarter price", "ربع كيلو"},
}


def generate_product_id(name: str) -> str:
    """Generate a product ID from the name."""
    slug = re.sub(r'\s+', '-', name.strip())
    slug = re.sub(r'[^\w\-]', '', slug, flags=re.UNICODE)
    return slug.lower()


def normalize_header(value) -> str:
    """Normalize Excel header text for Arabic and English matching."""
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def find_column_indexes(headers: list) -> dict:
    """Find required product columns by header name, independent of column order."""
    normalized_headers = [normalize_header(header) for header in headers]
    indexes = {}

    for field, aliases in HEADER_ALIASES.items():
        for idx, header in enumerate(normalized_headers):
            if header in aliases:
                indexes[field] = idx
                break

    return indexes


def is_blank(value) -> bool:
    """Return True when an Excel cell should be treated as empty."""
    return value is None or str(value).strip() == ""


def parse_price(value, required: bool = True):
    """Parse a price cell while allowing blank optional selling prices."""
    if is_blank(value):
        if required:
            raise ValueError("السعر مطلوب")
        return None

    if isinstance(value, (int, float)):
        return float(value)

    cleaned = str(value)
    cleaned = cleaned.replace(",", "")
    cleaned = cleaned.replace("جنيه", "")
    cleaned = cleaned.replace("EGP", "")
    cleaned = cleaned.strip()

    return float(cleaned)


def normalize_item_code(value) -> str:
    """Keep item codes clean, especially when Excel stores them as numbers."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, int):
        return str(value)
    return str(value).strip()


class CategorySelectDialog(ctk.CTkToplevel):
    """Dialog for selecting a category for a product."""

    def __init__(self, parent, product_name, categories):
        super().__init__(parent)
        self.title("اختر القسم")
        self.geometry("400x250")
        self.resizable(False, False)
        self.grab_set()

        self.categories = categories
        self.result = None

        self._build_form(product_name)

    def _build_form(self, product_name):
        """Build the category selection form."""
        frame = ctk.CTkFrame(self, fg_color=COLORS["surface"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text="اختر القسم للمنتج:",
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="ew", pady=(0, 6))

        ctk.CTkLabel(
            frame,
            text=product_name,
            font=(FONT_FAMILY, 13),
            text_color=COLORS["muted"],
        ).grid(row=1, column=0, sticky="ew", pady=(0, 14))

        category_names = [cat.get("name", "") for cat in self.categories]
        category_ids = [cat.get("id", "") for cat in self.categories]

        self.category_var = ctk.StringVar(value=category_names[0] if category_names else "")
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
        self.category_menu.grid(row=2, column=0, sticky="ew", pady=(0, 20))

        self.category_ids = category_ids

        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            button_frame,
            text="تأكيد",
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
        """Save the selected category."""
        category_name = self.category_var.get()
        try:
            idx = list(self.categories[i].get("name", "") for i in range(len(self.categories))).index(category_name)
            self.result = self.category_ids[idx]
        except ValueError:
            messagebox.showerror("خطأ", "اختر قسم صحيح")
            return

        self.destroy()


class ExcelPage(ctk.CTkFrame):
    """Page for importing and exporting Excel files."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.data_manager = DataManager()
        self.categories = []
        self.pending_imports = []
        self.import_rows = {}

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
            text="Excel",
            font=(FONT_FAMILY, 28, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 4))

        ctk.CTkLabel(
            header,
            text="استيراد وتصدير ملفات Excel.",
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
            text="📥 استيراد من Excel",
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLORS["green"],
            hover_color="#2E6B2F",
            text_color=COLORS["white"],
            command=self._import_excel,
        ).grid(row=0, column=0, padx=8)

        ctk.CTkButton(
            button_frame,
            text="📤 تصدير إلى Excel",
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLORS["blue"],
            hover_color="#3A7BC8",
            text_color=COLORS["white"],
            command=self._export_excel,
        ).grid(row=0, column=1, padx=8)

    def _build_content(self):
        """Build the main content area."""
        content = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=16)
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        info_frame = ctk.CTkFrame(content, fg_color=COLORS["surface"], corner_radius=12)
        info_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 12))
        info_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            info_frame,
            text="صيغة ملف Excel المتوقعة:",
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="e", padx=16, pady=(16, 8))

        columns_text = """
الأعمدة المطلوبة:
1. الكود / Item Code
2. الصنف / Name
3. البيع / Price
4. سعر الربع / Selling Price

ملاحظات:
• إذا كان سعر الربع موجوداً، سيتم عرضه للعميل كسعر المنتج
• إذا كان سعر الربع فارغاً، سيتم استخدام سعر البيع الأساسي
• المنتجات الموجودة سيتم تحديث أسعارها حسب الكود
• المنتجات الجديدة فقط ستُطلب لها اختيار قسم
        """

        ctk.CTkLabel(
            info_frame,
            text=columns_text,
            font=(FONT_FAMILY, 12),
            text_color=COLORS["muted"],
            justify="right",
            anchor="e",
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 16))

        review_frame = ctk.CTkFrame(content, fg_color=COLORS["surface"], corner_radius=12)
        review_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        review_frame.grid_columnconfigure(0, weight=1)
        review_frame.grid_rowconfigure(1, weight=1)

        review_header = ctk.CTkFrame(review_frame, fg_color="transparent")
        review_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        review_header.grid_columnconfigure(0, weight=1)

        self.review_status_label = ctk.CTkLabel(
            review_header,
            text="لم يتم تحميل ملف Excel بعد.",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        )
        self.review_status_label.grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(
            review_header,
            text="اعتماد الكل",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["green"],
            hover_color="#2E6B2F",
            text_color=COLORS["white"],
            command=self._approve_all_imports,
        ).grid(row=0, column=1, padx=(12, 0))

        self.review_scroll = ctk.CTkScrollableFrame(
            review_frame,
            fg_color=COLORS["white"],
            corner_radius=10,
        )
        self.review_scroll.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.review_scroll.grid_columnconfigure(0, weight=1)

    def _load_data(self):
        """Load categories from JSON."""
        self.categories = self.data_manager.get_categories()
        self._render_import_rows()

    def refresh(self):
        """Refresh category options when the page is shown."""
        self._load_data()

    def _import_excel(self):
        """Import products from Excel file."""
        file_path = filedialog.askopenfilename(
            title="اختر ملف Excel",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
        )

        if not file_path:
            return

        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb.active

            imported_products = []
            errors = []
            headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
            columns = find_column_indexes(headers)
            missing_fields = [
                field
                for field in ("code", "name", "price")
                if field not in columns
            ]

            if missing_fields:
                messagebox.showerror(
                    "خطأ",
                    "ملف Excel لا يحتوي على الأعمدة المطلوبة: الكود، الصنف، البيع",
                )
                return

            # Skip header row
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                item_code_value = row[columns["code"]]
                name_value = row[columns["name"]]

                if is_blank(item_code_value) or is_blank(name_value):
                    continue

                try:
                    item_code = normalize_item_code(item_code_value)
                    name = str(name_value).strip()
                    base_price = parse_price(row[columns["price"]], required=True)
                    selling_price = None

                    if "selling_price" in columns:
                        selling_price = parse_price(
                            row[columns["selling_price"]],
                            required=False,
                        )

                    display_price = selling_price if selling_price is not None else base_price

                    product = {
                        "id": item_code,
                        "name": name,
                        "price": display_price,
                        "basePrice": base_price,
                        "sellingPrice": selling_price,
                        "unit": "وحدة",
                        "categoryId": None,
                        "image": "",
                        "available": True,
                    }

                    imported_products.append(product)
                except (ValueError, TypeError) as e:
                    errors.append(f"صف {row_idx}: خطأ في البيانات - {str(e)}")

            if errors:
                error_msg = "\n".join(errors[:10])
                messagebox.showwarning("تحذيرات", f"بعض الصفوف بها مشاكل:\n{error_msg}")

            if not imported_products:
                messagebox.showerror("خطأ", "لم يتم العثور على منتجات صحيحة في الملف")
                return

            existing_products = self.data_manager.get_products()
            existing_by_id = {
                product.get("id"): product
                for product in existing_products
            }

            for product in imported_products:
                existing = existing_by_id.get(product.get("id"))
                if existing:
                    product["categoryId"] = existing.get("categoryId")
                    product["image"] = existing.get("image", "")
                    product["available"] = existing.get("available", True)

            self.pending_imports = imported_products
            self._render_import_rows()
            messagebox.showinfo(
                "تم التحميل",
                f"تم تحميل {len(imported_products)} منتج للمراجعة. راجع وعدل ثم اضغط اعتماد.",
            )

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل استيراد الملف: {str(e)}")

    def _render_import_rows(self):
        """Render editable pending Excel import rows."""
        if not hasattr(self, "review_scroll"):
            return

        for widget in self.review_scroll.winfo_children():
            widget.destroy()

        self.import_rows = {}
        pending_count = len(self.pending_imports)
        self.review_status_label.configure(
            text=f"قائمة المراجعة: {pending_count} منتج في انتظار الاعتماد"
            if pending_count
            else "لم يتم تحميل ملف Excel بعد."
        )

        if not pending_count:
            ctk.CTkLabel(
                self.review_scroll,
                text="استورد ملف Excel وستظهر المنتجات هنا كقائمة قابلة للتعديل.",
                font=(FONT_FAMILY, 13),
                text_color=COLORS["muted"],
            ).grid(row=0, column=0, sticky="ew", padx=14, pady=28)
            return

        header = ctk.CTkFrame(self.review_scroll, fg_color=COLORS["red"], corner_radius=8)
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        header.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for col, text in enumerate(("الكود", "الصنف", "السعر", "القسم")):
            ctk.CTkLabel(
                header,
                text=text,
                font=(FONT_FAMILY, 12, "bold"),
                text_color=COLORS["white"],
            ).grid(row=0, column=col, sticky="ew", padx=8, pady=8)

        for row_index, product in enumerate(self.pending_imports, start=1):
            self._create_import_row(row_index, product)

    def _create_import_row(self, row_index, product):
        """Create one editable product row in the import review list."""
        row = ctk.CTkFrame(self.review_scroll, fg_color=COLORS["surface"], corner_radius=10)
        row.grid(row=row_index, column=0, sticky="ew", padx=8, pady=4)
        row.grid_columnconfigure(1, weight=2)
        row.grid_columnconfigure((2, 3), weight=1)

        product_key = product.get("id")
        category_names = [category.get("name", "") for category in self.categories]
        category_ids = [category.get("id", "") for category in self.categories]
        current_category_name = ""

        if product.get("categoryId") in category_ids:
            current_category_name = category_names[category_ids.index(product.get("categoryId"))]
        elif category_names:
            current_category_name = category_names[0]

        code_label = ctk.CTkLabel(
            row,
            text=product_key,
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["text"],
        )
        code_label.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        name_entry = ctk.CTkEntry(
            row,
            font=(FONT_FAMILY, 12),
            fg_color=COLORS["white"],
            border_color=COLORS["beige"],
            border_width=1.5,
            justify="right",
        )
        name_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=8)
        name_entry.insert(0, product.get("name", ""))

        price_entry = ctk.CTkEntry(
            row,
            font=(FONT_FAMILY, 12),
            fg_color=COLORS["white"],
            border_color=COLORS["beige"],
            border_width=1.5,
            justify="right",
        )
        price_entry.grid(row=0, column=2, sticky="ew", padx=4, pady=8)
        price_entry.insert(0, str(product.get("price", "")))

        category_var = ctk.StringVar(value=current_category_name)
        category_menu = ctk.CTkComboBox(
            row,
            values=category_names,
            font=(FONT_FAMILY, 12),
            fg_color=COLORS["white"],
            border_color=COLORS["beige"],
            border_width=1.5,
            state="readonly",
            variable=category_var,
        )
        category_menu.grid(row=0, column=3, sticky="ew", padx=4, pady=8)

        action_frame = ctk.CTkFrame(row, fg_color="transparent")
        action_frame.grid(row=0, column=4, sticky="ew", padx=8, pady=8)

        ctk.CTkButton(
            action_frame,
            text="اعتماد",
            font=(FONT_FAMILY, 11, "bold"),
            fg_color=COLORS["green"],
            hover_color="#2E6B2F",
            text_color=COLORS["white"],
            width=76,
            command=lambda key=product_key: self._approve_import(key),
        ).grid(row=0, column=0, padx=2)

        ctk.CTkButton(
            action_frame,
            text="حذف",
            font=(FONT_FAMILY, 11, "bold"),
            fg_color=COLORS["red"],
            hover_color=COLORS["red_dark"],
            text_color=COLORS["white"],
            width=66,
            command=lambda key=product_key: self._discard_import(key),
        ).grid(row=0, column=1, padx=2)

        self.import_rows[product_key] = {
            "name": name_entry,
            "price": price_entry,
            "category": category_var,
        }

    def _read_import_row(self, product):
        """Build product data from an editable import row."""
        product_id = product.get("id")
        row = self.import_rows.get(product_id)

        if not row:
            return None

        name = row["name"].get().strip()
        category_name = row["category"].get().strip()

        if not name:
            messagebox.showerror("خطأ", "اسم المنتج مطلوب")
            return None
        if not category_name:
            messagebox.showerror("خطأ", "القسم مطلوب")
            return None

        try:
            display_price = parse_price(row["price"].get(), required=True)
        except ValueError:
            messagebox.showerror("خطأ", "السعر يجب أن يكون رقم")
            return None

        category_id = self._category_id_from_name(category_name)
        if not category_id:
            messagebox.showerror("خطأ", "القسم غير صحيح")
            return None

        updated_product = product.copy()
        updated_product["name"] = name
        updated_product["price"] = display_price
        updated_product["categoryId"] = category_id

        if updated_product.get("sellingPrice") is not None:
            updated_product["sellingPrice"] = display_price
        else:
            updated_product["basePrice"] = display_price

        return updated_product

    def _category_id_from_name(self, category_name):
        """Return category ID for the selected Arabic category name."""
        for category in self.categories:
            if category.get("name") == category_name:
                return category.get("id")
        return None

    def _approve_import(self, product_id):
        """Approve one product, save it, and remove it from the review list."""
        product = next((item for item in self.pending_imports if item.get("id") == product_id), None)
        if not product:
            return

        approved_product = self._read_import_row(product)
        if not approved_product:
            return

        if self._save_imported_products([approved_product], show_message=False):
            self.pending_imports = [
                item for item in self.pending_imports if item.get("id") != product_id
            ]
            self._render_import_rows()

    def _approve_all_imports(self):
        """Approve every valid product currently visible in the review list."""
        if not self.pending_imports:
            messagebox.showinfo("تنبيه", "لا توجد منتجات في قائمة المراجعة")
            return

        approved_products = []
        for product in self.pending_imports:
            approved_product = self._read_import_row(product)
            if not approved_product:
                return
            approved_products.append(approved_product)

        if self._save_imported_products(approved_products, show_message=True):
            self.pending_imports = []
            self._render_import_rows()

    def _discard_import(self, product_id):
        """Remove one product from the pending import list without saving it."""
        self.pending_imports = [
            item for item in self.pending_imports if item.get("id") != product_id
        ]
        self._render_import_rows()

    def _save_imported_products(self, products, show_message=True):
        """Save imported products to JSON."""
        saved_count = 0
        updated_count = 0
        data = self.data_manager.load()
        existing_products = data.setdefault("products", [])
        product_indexes = {
            product.get("id"): idx
            for idx, product in enumerate(existing_products)
        }

        for product in products:
            product_id = product.get("id")

            if product_id in product_indexes:
                existing = existing_products[product_indexes[product_id]].copy()
                existing.update(
                    {
                        "name": product.get("name", existing.get("name", "")),
                        "price": product.get("price", existing.get("price", 0)),
                        "basePrice": product.get("basePrice"),
                        "sellingPrice": product.get("sellingPrice"),
                        "unit": product.get("unit", existing.get("unit", "وحدة")),
                    }
                )
                existing_products[product_indexes[product_id]] = existing
                updated_count += 1
                continue

            existing_products.append(product)
            saved_count += 1

        if self.data_manager.save(data):
            self._load_data()
            if show_message:
                messagebox.showinfo(
                    "نجح",
                    f"تم استيراد {saved_count} منتج جديد.\nتم تحديث {updated_count} منتج موجود.",
                )
            return True

        messagebox.showerror("خطأ", "فشل حفظ بيانات الاستيراد")
        return False

    def _export_excel(self):
        """Export all products to Excel file."""
        file_path = filedialog.asksaveasfilename(
            title="احفظ ملف Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
        )

        if not file_path:
            return

        try:
            products = self.data_manager.get_products()

            wb = Workbook()
            ws = wb.active
            ws.title = "Products"

            # Add headers
            headers = ["الكود", "الصنف", "البيع", "سعر الربع"]
            ws.append(headers)

            # Style header row
            header_fill = PatternFill(start_color="AD263C", end_color="AD263C", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF")

            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Add products
            for product in products:
                base_price = product.get("basePrice", product.get("price", 0))
                selling_price = product.get("sellingPrice")

                ws.append([
                    product.get("id", ""),
                    product.get("name", ""),
                    base_price,
                    selling_price if selling_price is not None else "",
                ])

            # Adjust column widths
            ws.column_dimensions["A"].width = 20
            ws.column_dimensions["B"].width = 25
            ws.column_dimensions["C"].width = 12
            ws.column_dimensions["D"].width = 14

            wb.save(file_path)
            messagebox.showinfo("نجح", f"تم تصدير {len(products)} منتج بنجاح.")

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل تصدير الملف: {str(e)}")
