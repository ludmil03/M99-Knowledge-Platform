import os
import requests
from .parser import parse_product_page

class BultexB2BClient:
    def __init__(self, base_url="https://b2b.bultex99.com:8823"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def credentials_from_env(self):
        keys = ["BULTEX_B2B_CLIENT_CODE","BULTEX_B2B_USERNAME","BULTEX_B2B_PASSWORD"]
        vals = [os.getenv(k,"") for k in keys]
        if not all(vals):
            raise RuntimeError("Missing Bultex B2B credentials in environment variables")
        return tuple(vals)

    def login(self):
        raise NotImplementedError("Login POST field names must be confirmed first")

    def fetch_product_html(self, product_id):
        r = self.session.get(f"{self.base_url}/pap/minfo.php", params={"i":product_id}, timeout=30)
        r.raise_for_status()
        return r.text

    def parse_product(self, html, product_id, warehouse_code, warehouse_name):
        return parse_product_page(
            html,
            f"{self.base_url}/pap/minfo.php?i={product_id}",
            warehouse_code,
            warehouse_name,
        )
