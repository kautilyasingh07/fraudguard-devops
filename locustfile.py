from locust import HttpUser, between, task


FRAUD_PAYLOAD = {
    "TransactionAmt": 1500.0,
    "TransactionDT": 90986,
    "ProductCD": "W",
    "card1": 9500,
    "card2": 117.0,
    "card3": 150.0,
    "card4": "visa",
    "card5": 226.0,
    "card6": "debit",
    "addr1": 299.0,
    "addr2": 87.0,
    "dist1": 0.0,
    "P_emaildomain": "gmail.com",
    "R_emaildomain": "gmail.com",
    "V1": 1.0,
    "V2": 1.0,
    "V3": 1.0,
    "V4": 1.0,
    "V5": 1.0,
    "V6": 1.0,
    "V7": 1.0,
    "V8": 0.0,
    "V9": 0.0,
    "V10": 0.0,
    "V11": 0.0,
    "V12": 1.0,
    "V13": 1.0,
    "V14": 1.0,
    "V15": 0.0,
    "V16": 0.0,
    "V17": 0.0,
}


class FraudGuardUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(8)
    def predict(self):
        try:
            self.client.post("/predict", json=FRAUD_PAYLOAD, name="/predict")
        except Exception as exc:
            print(f"[Locust] predict connection error: {exc}")

    @task(2)
    def health_check(self):
        self.client.get("/health", name="/health")
