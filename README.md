# Event-Driven System and Pipes-and-Filters Architecture

This project implements an event-driven system using RabbitMQ and rebuilds it as a pipes-and-filters architecture. The system is designed to process user-submitted messages through a series of services, applying filtering and transformation before publishing the final output via email.

---

## Introduction

The objective of this project is to:

1. Build a distributed **event-driven system** that processes user messages through a series of services using RabbitMQ as the message broker.
2. Rebuild the system as a **pipes-and-filters** architecture, combining services into a single deployable application with filters running in separate processes.
3. Compare the performance between the two architectures by load-testing and analyzing differences in time behavior, resource utilization, and capacity.

---

## Project Structure

```perl
event-driven-system/
├── LoadTestingReport-Documentation/   # Contains the performance report
├── locust/                            # Contains Locust load testing files
│   ├── Dockerfile
│   └── locustfile.py
├── Solutions/
│   ├── Distributed/                   # Event-driven system services
│   │   ├── api_service/
│   │   ├── filter_service/
│   │   ├── publish_service/
│   │   └── screaming_service/
│   └── Monolithic/                    # Pipes-and-filters system
│       └── main.py
├── docker-compose.yml                 # Docker Compose file for event-driven system
└── docker-compose.monolithic.yml      # Docker Compose file for pipes-and-filters system
```

---

## Setup and Installation

1. **Prerequisites**:
    - Docker installed on your machine.
    - Docker Compose installed.
    - An SMTP server or service credentials for sending emails (e.g., Gmail SMTP).
2. **Clone the Repository**:
    
    ```bash
    git clone https://github.com/MohamadSafi/event-driven-system.git
    cd event-driven-system
    ```
    
3. **Environment Variables**:
    - Create a `.env` file in the root directory.
    
    Add your SMTP configuration:
    
    ```
    SMTP_SERVER=smtp.example.com
    SMTP_PORT=465
    SMTP_USER=your_email@example.com
    SMTP_PASSWORD=your_email_password
    RECIPIENTS=recipient1@example.com,recipient2@example.com
    ```
    
    - Replace the placeholders with your actual SMTP details.

---

## Running the Systems

### Event-Driven System

1. **Navigate to the Project Directory**:
    
    ```bash
    cd event-driven-system
    ```
    
2. **Build and Run the Services**:
    
    ```bash
    docker-compose up --build
    ```
    
3. **Access the API Service**:
    
    The API service will be running on `http://localhost:5001`.
    
4. **Send a Test Message**:
    
    ```bash
    curl -X POST -H "Content-Type: application/json" \
    -d '{"alias": "testuser", "message": "This is a test message"}' \
    http://localhost:5001/submit
    ```
    

### Pipes-and-Filters System

1. **Navigate to the Project Directory**:
    
    ```bash
    cd event-driven-system
    ```
    
2. **Build and Run the Monolithic Service**:
    
    ```bash
    docker-compose -f docker-compose.monolithic.yml up --build
    ```
    
3. **Access the Monolithic API Service**:
    
    The service will be running on `http://localhost:5001`.
    
4. **Send a Test Message**:
    
    ```bash
    curl -X POST -H "Content-Type: application/json" \
    -d '{"alias": "testuser", "message": "This is a test message"}' \
    http://localhost:5001/submit
    ```
    

---

## Load Testing with Locust

Locust is used to perform load testing on both systems to compare performance.

1. **Access the Locust Web Interface**:
    
    Open `http://localhost:8089` in your web browser.
    
2. **Configure Test Parameters**:
    - Number of total users to simulate.
    - Spawn rate (users per second).
3. **Start the Test**:
    - Click on the **Start swarming** button.
4. **Monitoring and Results**:
    - Monitor real-time statistics and results on the Locust web interface.
    - Analyze the performance metrics collected.

---

## Important Notes

- **Stop-Words Filtering**:
    - The system filters out messages containing the following stop-words:
        
        ```
        bird-watching
        ailurophobia
        mango
        ```
        
- **Email Sending**:
    - Ensure you have valid SMTP credentials.
- **Logging**:
    - The application includes logging to track the processing flow and errors.
    - Logs can be viewed in the Docker container output.

---

## Load Testing Report

For more information, see the [Load Testing Report Documentation](./LoadTestingReport-Documentation/README.md).

---

## Demo

YouTube [Link](https://youtu.be/ATnr0La9qo8)
