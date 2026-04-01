"""
Incident Response Multi-Agent System - Shared State
"""
from typing import TypedDict, List, Dict, Optional

class IncidentState(TypedDict):
    """Shared state for all agents in incident response workflow."""

    # Input
    log_content: str                      # Original error log

    # Routing
    next_agent: str                       # Which agent to call next

    # Agent Results
    log_analysis: Optional[str]           # From Log Analyzer
    root_cause: Optional[str]             # From Root Cause Investigator
    solution: Optional[str]               # From Solution Recommender

    # Final Output
    incident_report: str                  # Compiled by Supervisor

    # Metadata
    steps_completed: List[str]            # Track progress
    errors: List[str]                     # Track errors
