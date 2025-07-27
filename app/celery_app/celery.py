"""
Celery Application Instance
"""

import os
from celery import Celery
from app.celery_app.config import CeleryConfig


def create_celery_app() -> Celery:
    """Create and configure Celery application"""
    
    celery_app = Celery("story_teller")
    
    # Load configuration
    celery_app.config_from_object(CeleryConfig)
    
    # Auto-discover tasks
    celery_app.autodiscover_tasks([
        'app.celery_app.tasks.stories',
        'app.celery_app.tasks.llm',
    ])
    
    # Task discovery for testing
    celery_app.conf.update(
        include=[
            'app.celery_app.tasks.stories',
            'app.celery_app.tasks.llm',
        ]
    )
    
    return celery_app


# Create the Celery app instance
celery_app = create_celery_app()


# Task base configuration for shared functionality
class BaseTask(celery_app.Task):
    """Base task class with common functionality"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        print(f"Task {task_id} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        print(f"Task {task_id} succeeded")
        super().on_success(retval, task_id, args, kwargs)
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry"""
        print(f"Task {task_id} retrying: {exc}")
        super().on_retry(exc, task_id, args, kwargs, einfo)


# Set the base task class
celery_app.Task = BaseTask

if os.getenv("DEBUG_CELERY") and int(os.getenv("DEBUG_CELERY")) == 1:
    import debugpy

    debugpy.listen(("0.0.0.0", 5678))
    print("🔴 Debugging is enabled. Waiting for debugger to attach...")
    debugpy.wait_for_client()
