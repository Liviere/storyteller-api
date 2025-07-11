"""
Locust configuration file for Story Teller API performance testing.

This file contains predefined configurations for different types of load tests.
"""

# Configuration for different test scenarios

# Light load test - for development and quick checks
LIGHT_LOAD = {
    "users": 10,
    "spawn_rate": 2,
    "run_time": "2m",
    "description": "Light load test for development",
}

# Medium load test - for staging environment
MEDIUM_LOAD = {
    "users": 50,
    "spawn_rate": 5,
    "run_time": "5m",
    "description": "Medium load test for staging",
}

# Heavy load test - for production readiness
HEAVY_LOAD = {
    "users": 200,
    "spawn_rate": 10,
    "run_time": "10m",
    "description": "Heavy load test for production readiness",
}

# Stress test - to find breaking points
STRESS_TEST = {
    "users": 500,
    "spawn_rate": 20,
    "run_time": "5m",
    "description": "Stress test to find system limits",
}

# Spike test - sudden traffic increases
SPIKE_TEST = {
    "users": 100,
    "spawn_rate": 50,  # Very fast spawn rate
    "run_time": "3m",
    "description": "Spike test for sudden traffic",
}

# Endurance test - long running
ENDURANCE_TEST = {
    "users": 30,
    "spawn_rate": 3,
    "run_time": "30m",
    "description": "Endurance test for stability",
}
