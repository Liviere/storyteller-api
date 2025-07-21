"""
Task Service for managing Celery tasks
"""

from typing import Dict, Any, Optional
from celery.result import AsyncResult
from app.celery_app.celery import celery_app


class TaskService:
    """Service for managing asynchronous tasks"""
    
    def __init__(self):
        self.celery_app = celery_app
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a task
        
        Args:
            task_id: Task ID to check
            
        Returns:
            Dictionary with task status information
        """
        task_result = AsyncResult(task_id, app=self.celery_app)
        
        return {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None,
            "info": task_result.info,
            "traceback": task_result.traceback,
            "successful": task_result.successful() if task_result.ready() else None,
            "failed": task_result.failed() if task_result.ready() else None,
        }
    
    def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """
        Get the result of a completed task
        
        Args:
            task_id: Task ID to get result for
            timeout: Maximum time to wait for result
            
        Returns:
            Task result or raises exception if task failed
        """
        task_result = AsyncResult(task_id, app=self.celery_app)
        return task_result.get(timeout=timeout)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending task
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            True if task was cancelled, False otherwise
        """
        task_result = AsyncResult(task_id, app=self.celery_app)
        task_result.revoke(terminate=True)
        return True
    
    def get_active_tasks(self) -> Dict[str, Any]:
        """
        Get information about currently active tasks
        
        Returns:
            Dictionary with active tasks information
        """
        inspect = self.celery_app.control.inspect()
        return {
            "active": inspect.active(),
            "scheduled": inspect.scheduled(),
            "reserved": inspect.reserved(),
        }
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """
        Get statistics about Celery workers
        
        Returns:
            Dictionary with worker statistics
        """
        inspect = self.celery_app.control.inspect()
        return {
            "stats": inspect.stats(),
            "ping": inspect.ping(),
            "registered": inspect.registered(),
        }
    
    # Story-related task helpers
    def create_story_async(self, story_data: Dict[str, Any]) -> str:
        """Submit story creation task"""
        task = self.celery_app.send_task(
            'stories.create_story',
            args=[story_data]
        )
        return task.id
    
    def update_story_async(self, story_id: int, story_data: Dict[str, Any], retry_config: Optional[Dict[str, Any]] = None) -> str:
        """
        Submit story update task
        
        Args:
            story_id: ID of the story to update
            story_data: Data to update
            retry_config: Optional retry configuration (for testing)
                         Example: {"max_retries": 0, "countdown": 1}
        """
        no_retry = retry_config is not None and retry_config.get("retry") is False
            
        task = self.celery_app.send_task(
            'stories.update_story',
            args=[story_id, story_data, no_retry]
        )
        return task.id
    
    def delete_story_async(self, story_id: int, retry_config: Optional[Dict[str, Any]] = None) -> str:
        """
        Submit story deletion task
        
        Args:
            story_id: ID of the story to delete
            retry_config: Optional retry configuration (for testing)
                         Example: {"max_retries": 0, "countdown": 1}
        """
        no_retry = retry_config is not None and retry_config.get("retry") is False
            
        task = self.celery_app.send_task(
            'stories.delete_story',
            args=[story_id, no_retry]
        )
        return task.id
    
    def patch_story_async(self, story_id: int, patch_data: Dict[str, Any]) -> str:
        """Submit story patch task"""
        task = self.celery_app.send_task(
            'stories.patch_story',
            args=[story_id, patch_data]
        )
        return task.id
    
    # LLM-related task helpers
    def generate_story_async(self, **kwargs) -> str:
        """Submit story generation task"""
        task = self.celery_app.send_task(
            'llm.generate_story',
            kwargs=kwargs
        )
        return task.id
    
    def analyze_story_async(self, **kwargs) -> str:
        """Submit story analysis task"""
        task = self.celery_app.send_task(
            'llm.analyze_story',
            kwargs=kwargs
        )
        return task.id
    
    def summarize_story_async(self, **kwargs) -> str:
        """Submit story summarization task"""
        task = self.celery_app.send_task(
            'llm.summarize_story',
            kwargs=kwargs
        )
        return task.id
    
    def improve_story_async(self, **kwargs) -> str:
        """Submit story improvement task"""
        task = self.celery_app.send_task(
            'llm.improve_story',
            kwargs=kwargs
        )
        return task.id


# Global task service instance
task_service = TaskService()


def get_task_service() -> TaskService:
    """Get the global task service instance"""
    return task_service
