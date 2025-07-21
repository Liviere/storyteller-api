#!/usr/bin/env python3
"""
Celery Worker Script

Script to start Celery workers for the Story Teller API.
This script should be used to run background task workers.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the Celery app
from app.celery_app.celery import celery_app

if __name__ == "__main__":
    # Set up logging
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Start the worker
    celery_app.start()
