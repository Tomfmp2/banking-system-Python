from typing import List
from models.product import Product
from models.account import Account
from database.json_handler import JsonHandler

class ProductService:
    def __init__(self, db_handler: JsonHandler):
        self.db = db_handler

    def get_all_products(self) -> List[Product]:
        data = self.db.read()
        return [Product.from_dict(p) for p in data.get("products", [])]

    def _save_products(self, products: List[Product]) -> None:
        self.db.write("products", [p.to_dict() for p in products])

    def get_products_by_account(self, account_id: str) -> List[Product]:
        return [p for p in self.get_all_products() if p.account_id == account_id]

    def create_product(self, account: Account, category: str, prod_type: str, details: dict) -> Product:
        product = Product(
            account_id=account.account_id,
            product_category=category,
            product_type=prod_type,
            details=details
        )
        products = self.get_all_products()
        products.append(product)
        self._save_products(products)
        return product
