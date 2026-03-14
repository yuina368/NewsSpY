from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from datetime import datetime
import logging

from app.services.json_storage import write_status, read_status
from batch.main import NewsSpYBatchProcessor

logger = logging.getLogger(__name__)
router = APIRouter(tags=["batch"])

# Global task status
task_status: Dict[str, Dict[str, Any]] = {}


def run_batch_task(task_id: str):
    """Run batch processing in background"""
    try:
        task_status[task_id] = {
            "status": "running",
            "step": "initializing",
            "progress": 0,
            "message": "Starting batch processing...",
            "started_at": datetime.now().isoformat()
        }

        # Run the batch processor
        processor = NewsSpYBatchProcessor()

        # Update progress
        task_status[task_id]["step"] = "fetching"
        task_status[task_id]["progress"] = 30
        task_status[task_id]["message"] = "Fetching articles..."

        # The processor.run() will handle all steps
        processor.run()

        # Get final status
        final_status = read_status()

        task_status[task_id]["step"] = "completed"
        task_status[task_id]["progress"] = 100
        task_status[task_id]["message"] = "Batch processing completed successfully"
        task_status[task_id]["completed_at"] = datetime.now().isoformat()
        task_status[task_id]["status"] = "completed"
        task_status[task_id]["articles_fetched"] = final_status.get("articles_count", 0)
        task_status[task_id]["articles_added"] = final_status.get("articles_count", 0)
        task_status[task_id]["articles_analyzed"] = final_status.get("analyzed_count", 0)
        task_status[task_id]["companies_registered"] = final_status.get("companies_count", 0)
        task_status[task_id]["scores_saved"] = final_status.get("scores_count", 0)

    except Exception as e:
        logger.exception("Batch processing failed")
        task_status[task_id]["status"] = "failed"
        task_status[task_id]["message"] = f"Error: {str(e)}"
        task_status[task_id]["completed_at"] = datetime.now().isoformat()


@router.post("/batch/run")
async def run_batch(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """Start batch processing in background"""
    import uuid
    task_id = str(uuid.uuid4())

    background_tasks.add_task(run_batch_task, task_id)

    return {
        "task_id": task_id,
        "status": "started",
        "message": "Batch processing started in background"
    }


@router.get("/batch/status/{task_id}")
async def get_batch_status(task_id: str) -> Dict[str, Any]:
    """Get status of a batch task"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")

    return task_status[task_id]


@router.get("/batch/status")
async def get_current_status() -> Dict[str, Any]:
    """Get current system status"""
    status = read_status()
    return status
