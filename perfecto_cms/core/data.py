import json
import logging
from datetime import datetime
from pathlib import Path

from perfecto_cms.core.paths import BACKUP_DIR, DATA_FILE


logger = logging.getLogger("perfecto_cms")


class DataManager:
    """Manages products.json file operations with automatic backups."""

    def __init__(self):
        self.data_file = DATA_FILE
        self.backup_dir = BACKUP_DIR

    def load(self) -> dict:
        """Load products.json and return the data."""
        if not self.data_file.exists():
            logger.warning("Data file not found, returning empty structure")
            return {"meta": {}, "categories": [], "products": []}

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load data file: {e}")
            return {"meta": {}, "categories": [], "products": []}

    def save(self, data: dict) -> bool:
        """Save data to products.json and create a backup."""
        try:
            # Create backup
            self._create_backup()

            # Write new data
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info("Data saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            return False

    def _create_backup(self) -> None:
        """Create a backup of the current data file."""
        if not self.data_file.exists():
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_file = self.backup_dir / f"products.backup.{timestamp}.json"
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            with open(self.data_file, "r", encoding="utf-8") as f:
                backup_data = json.load(f)

            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Backup created: {backup_file}")
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")

    def get_categories(self) -> list:
        """Get all categories."""
        data = self.load()
        return data.get("categories", [])

    def get_products(self) -> list:
        """Get all products."""
        data = self.load()
        return data.get("products", [])

    def add_product(self, product: dict) -> bool:
        """Add a new product."""
        data = self.load()

        data.setdefault("products", []).append(product)
        return self.save(data)

    def update_product(self, product_id: str, product: dict) -> bool:
        """Update an existing product."""
        data = self.load()
        products = data.get("products", [])

        for i, p in enumerate(products):
            if p["id"] == product_id:
                products[i] = product
                return self.save(data)

        logger.warning(f"Product with ID {product_id} not found")
        return False

    def delete_product(self, product_id: str) -> bool:
        """Delete a product."""
        data = self.load()
        products = data.get("products", [])
        original_count = len(products)

        data["products"] = [p for p in products if p["id"] != product_id]

        if len(data["products"]) == original_count:
            logger.warning(f"Product with ID {product_id} not found")
            return False

        return self.save(data)

    def add_category(self, category: dict) -> bool:
        """Add a new category."""
        data = self.load()
        data.setdefault("categories", []).append(category)
        return self.save(data)

    def update_category(self, category_id: str, category: dict) -> bool:
        """Update an existing category."""
        data = self.load()
        categories = data.get("categories", [])

        for i, c in enumerate(categories):
            if c["id"] == category_id:
                categories[i] = category
                return self.save(data)

        logger.warning(f"Category with ID {category_id} not found")
        return False

    def delete_category(self, category_id: str) -> bool:
        """Delete a category."""
        data = self.load()
        categories = data.get("categories", [])
        original_count = len(categories)

        data["categories"] = [c for c in categories if c["id"] != category_id]

        if len(data["categories"]) == original_count:
            logger.warning(f"Category with ID {category_id} not found")
            return False

        return self.save(data)
