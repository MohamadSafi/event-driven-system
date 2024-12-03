from locust import HttpUser, task, between
import json
import random

class APIUser(HttpUser):
    wait_time = between(1, 3)  # Random wait between requests (1-3 seconds)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aliases = ["user1", "user2", "user3", "user4", "user5"]
        self.messages = [
            "Hello, world!",
            "I love bird-watching in the park",
            "Testing the API",
            "I have ailurophobia and it's terrible",
            "Final test message",
            "My favorite fruit is mango",
            "Load testing is fun",
            "Just another message",
            "Testing the filter service",
            "This message should pass through"
        ]
    
    @task
    def submit_message(self):
        payload = {
            "alias": random.choice(self.aliases),
            "message": random.choice(self.messages)
        }
        headers = {"Content-Type": "application/json"}
        self.client.post("/submit", json=payload, headers=headers)