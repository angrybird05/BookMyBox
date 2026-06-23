import random
from datetime import date, timedelta
from locust import HttpUser, task, between


class BookMyBoxUser(HttpUser):
    """Simulates a typical customer browsing grounds, checking slots, and using the system."""

    wait_time = between(1, 5)  # Simulate human delay between tasks (1 to 5 seconds)
    token = None
    user_id = None
    ground_ids = []

    def on_start(self):
        """Perform user setup - register/login to obtain authentication tokens."""
        # Setup test credentials
        self.email = f"loadtest_{random.randint(10000, 99999)}@example.com"
        self.password = "Secr3tPa$$word!"
        self.phone = f"+91{random.randint(7000000000, 9999999999)}"
        self.name = "Load Test User"
        self.city = "Mumbai"

        # 1. Register User
        register_payload = {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "password": self.password,
            "city": self.city,
        }
        
        # In mock OTP mode, we can register and verify directly.
        try:
            with self.client.post("/api/v1/auth/register", json=register_payload, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                elif response.status_code == 400 and "already registered" in response.text:
                    response.success()  # Already exists, we can proceed
                else:
                    response.failure(f"Registration failed with code {response.status_code}: {response.text}")
                    return
        except Exception as e:
            print(f"Exception during registration: {e}")
            return

        # 2. Verify OTP (using the dev-friendly mock OTP '123456')
        verify_payload = {
            "email": self.email,
            "otp": "123456"
        }
        try:
            with self.client.post("/api/v1/auth/verify-otp", json=verify_payload, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    # If already verified, we might get 400. That's fine.
                    response.success()
        except Exception:
            pass

        # 3. Login User
        login_payload = {
            "username": self.email,
            "password": self.password,
        }
        try:
            with self.client.post("/api/v1/auth/login", data=login_payload, catch_response=True) as response:
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    self.token = data.get("access_token")
                    self.client.headers.update({"Authorization": f"Bearer {self.token}"})
                    response.success()
                else:
                    response.failure(f"Login failed with code {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Exception during login: {e}")

        # Fetch some ground IDs to perform detailed browses
        try:
            with self.client.get("/api/v1/grounds", catch_response=True) as response:
                if response.status_code == 200:
                    grounds_data = response.json().get("data", {}).get("items", [])
                    self.ground_ids = [g.get("id") for g in grounds_data]
                    response.success()
        except Exception:
            pass

    @task(5)
    def browse_grounds(self):
        """Simulate browsing the main grounds listing with pagination and filters."""
        params = {
            "page": 1,
            "per_page": 10,
            "city": "Mumbai",
            "sort_by": "rating"
        }
        self.client.get("/api/v1/grounds", params=params, name="/api/v1/grounds")

    @task(4)
    def view_top_grounds(self):
        """Simulate viewing top grounds cards on the home page (uses cached endpoint)."""
        self.client.get("/api/v1/grounds/top", name="/api/v1/grounds/top")

    @task(3)
    def view_ground_details(self):
        """Simulate checking a specific ground page if any exist."""
        if self.ground_ids:
            ground_id = random.choice(self.ground_ids)
            self.client.get(f"/api/v1/grounds/{ground_id}", name="/api/v1/grounds/{id}")
            
            # Fetch slots for tomorrow
            tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
            self.client.get(
                f"/api/v1/grounds/{ground_id}/slots?date={tomorrow}", 
                name="/api/v1/grounds/{id}/slots"
            )

    @task(2)
    def view_dashboard_and_wallet(self):
        """Simulate a logged-in user viewing their dashboard stats and wallet transactions."""
        if not self.token:
            return
            
        self.client.get("/api/v1/users/me/stats", name="/api/v1/users/me/stats")
        self.client.get("/api/v1/wallet", name="/api/v1/wallet")
        self.client.get("/api/v1/wallet/transactions", name="/api/v1/wallet/transactions")

    @task(1)
    def simulate_wallet_topup(self):
        """Simulate wallet top-up."""
        if not self.token:
            return
            
        topup_payload = {
            "amount": 1000,
            "payment_method": "UPI"
        }
        self.client.post("/api/v1/wallet/topup", json=topup_payload, name="/api/v1/wallet/topup")
