"""
Background tasks module for EduNova

This module provides functionality for running background tasks,
such as processing documents for the knowledge base.
"""

from backend.tasks.rag_processor import start_processing_queue_item 