import random
import json
from locust import HttpUser, task, between

# Product IDs from the actual products.json file
PRODUCT_IDS = [
    "OLJCESPC7Z",  # Sunglasses
    "66VCHSJNUP",  # Tank Top
    "1YMWWN1N4O",  # Watch
    "L9ECAV7KIM",  # Loafers
    "2ZYFJ3GM2N",  # Hairdryer
    "0PUK6V6EV0",  # Candle Holder
    "LS4PSXUNUM",  # Salt & Pepper Shakers
    "9SIQT8TOJO",  # Bamboo Glass Jar
    "6E92ZMYYFZ",  # Mug
]

# Supported currencies from the Go code
CURRENCIES = ["USD", "EUR", "CAD", "JPY", "GBP", "TRY"]

class BoutiqueUser(HttpUser):
    wait_time = between(2, 5)
    
    # Increase timeout for unstable connections
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.timeout = 30
    
    def on_start(self):
        """Initialize user session"""
        # Warm up session by visiting home page
        with self.client.get("/", name="GET / (warmup)", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 0:
                response.failure("Connection failed - server may be down")
            else:
                response.failure(f"Home page failed with status {response.status_code}")

    @task(5)
    def browse_home(self):
        """Browse the home page - most common action"""
        with self.client.get("/", name="GET /", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 0:
                response.failure("Connection failed - server may be down")
            else:
                response.failure(f"Home page failed with status {response.status_code}")

    @task(3)
    def view_product(self):
        """View a specific product page"""
        product_id = random.choice(PRODUCT_IDS)
        with self.client.get(f"/product/{product_id}", name="GET /product/:id", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 500:
                response.failure("Product page returned 500 - server error")
            else:
                response.failure(f"Product page failed with status {response.status_code}")

    @task(2)
    def view_cart(self):
        """View shopping cart"""
        with self.client.get("/cart", name="GET /cart", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Cart page failed with status {response.status_code}")

    @task(2)
    def add_to_cart(self):
        """Add item to cart"""
        product_id = random.choice(PRODUCT_IDS)
        quantity = random.randint(1, 3)
        
        payload = {
            "product_id": product_id,
            "quantity": quantity
        }
        
        with self.client.post("/cart", data=payload, name="POST /cart", catch_response=True) as response:
            if response.status_code in [200, 302]:  # 302 is redirect after successful add
                response.success()
            elif response.status_code == 500:
                response.failure("Add to cart returned 500 - server error")
            else:
                response.failure(f"Add to cart failed with status {response.status_code}")

    @task(1)
    def change_currency(self):
        """Change currency preference"""
        currency = random.choice(CURRENCIES)
        payload = {"currency_code": currency}
        
        with self.client.post("/setCurrency", data=payload, name="POST /setCurrency", catch_response=True) as response:
            if response.status_code in [200, 302]:  # 302 is redirect after successful change
                response.success()
            else:
                response.failure(f"Currency change failed with status {response.status_code}")

    @task(1)
    def empty_cart(self):
        """Empty the shopping cart"""
        with self.client.post("/cart/empty", name="POST /cart/empty", catch_response=True) as response:
            if response.status_code in [200, 302]:  # 302 is redirect after successful empty
                response.success()
            else:
                response.failure(f"Empty cart failed with status {response.status_code}")

    @task(1)
    def checkout_flow(self):
        """Complete checkout process"""
        # First, add an item to cart
        product_id = random.choice(PRODUCT_IDS)
        add_payload = {
            "product_id": product_id,
            "quantity": 1
        }
        
        with self.client.post("/cart", data=add_payload, name="POST /cart (checkout prep)", catch_response=True) as response:
            if response.status_code not in [200, 302]:
                response.failure(f"Failed to add item for checkout: {response.status_code}")
                return
        
        # Then proceed to checkout
        checkout_payload = {
            "email": f"user{random.randint(1000, 9999)}@example.com",
            "street_address": f"{random.randint(100, 999)} Main St",
            "zip_code": random.randint(10000, 99999),
            "city": "San Francisco",
            "state": "CA",
            "country": "United States",
            "credit_card_number": "4111111111111111",
            "credit_card_expiration_month": "12",
            "credit_card_expiration_year": "2025",
            "credit_card_cvv": "123"
        }
        
        with self.client.post("/cart/checkout", data=checkout_payload, name="POST /cart/checkout", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 500:
                response.failure("Checkout returned 500 - server error")
            else:
                response.failure(f"Checkout failed with status {response.status_code}")

    @task(1)
    def logout(self):
        """Logout user"""
        with self.client.get("/logout", name="GET /logout", catch_response=True) as response:
            if response.status_code in [200, 302]:  # 302 is redirect after logout
                response.success()
            else:
                response.failure(f"Logout failed with status {response.status_code}")

    @task(1)
    def access_static_resources(self):
        """Access static resources like CSS, JS, images"""
        static_resources = [
            "/static/styles/styles.css",
            "/static/styles/cart.css",
            "/static/styles/order.css",
            "/static/favicon.ico",
            "/static/img/products/sunglasses.jpg",
            "/static/img/products/watch.jpg",
        ]
        
        resource = random.choice(static_resources)
        with self.client.get(resource, name="GET /static/*", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Static resource failed with status {response.status_code}")