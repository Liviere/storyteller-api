"""
Celery Configuration
"""

import os
from kombu import Queue, Exchange


class CeleryConfig:
    """Celery configuration class"""
    
    # Broker settings
    broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
    
    # Connection pool settings
    broker_pool_limit = 20
    broker_connection_retry_on_startup = True
    broker_connection_retry = True
    broker_connection_max_retries = 10
    
    # Task settings
    task_serializer = "json"
    result_serializer = "json"
    accept_content = ["json"]
    timezone = "UTC"
    enable_utc = True
    
    # Performance optimizations
    task_acks_late = True
    worker_prefetch_multiplier = 1
    task_reject_on_worker_lost = True
    
    # Retry configuration
    task_default_retry_delay = 60
    task_max_retries = 3
    
    # Result backend settings
    result_expires = 3600  # 1 hour
    result_persistent = True
    
    # Queue configuration with priority
    task_routes = {
        'app.celery_app.tasks.stories.*': {'queue': 'stories'},
    }
    
    task_default_queue = 'default'
    task_queues = [
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('stories', Exchange('stories'), routing_key='stories'),
    ]
    
    # Monitoring
    worker_send_task_events = True
    task_send_sent_event = True
    
    # Redis-specific optimizations
    broker_transport_options = {
        'visibility_timeout': 3600,  # 1 hour
        'fanout_prefix': True,
        'fanout_patterns': True,
    }
    
    result_backend_transport_options = {
        'retry_policy': {'timeout': 5.0}
    }
