"""
Hint generation and management API endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, Optional
import logging

from src.schemas.learning import (
    HintRequest, HintResponse, HintContext, HintUsageLog, 
    HintTriggerSession, StudentHintProfile
)
from src.services.hint_generation_service import HintGenerationService
from src.services.coin_management_service import CoinManagementService
from src.services.student_profile_service import StudentProfileService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/request", response_model=HintResponse)
async def request_hint(
    request: HintRequest,
    hint_service: HintGenerationService = Depends()
):
    """
    Request a hint for current learning context
    
    Supports tiered hint system with coin-based economy:
    - Level 1: Conceptual Guidance (1 coin)
    - Level 2: Directional Hints (2 coins)  
    - Level 3: Implementation Hints (3 coins)
    - Level 4: Complete Solution (5 coins)
    """
    try:
        logger.info(f"Hint request: student {request.student_id}, level {request.level}")
        
        # Validate hint level
        if request.level < 0 or request.level > 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hint level must be between 0-4 (0 = auto-determine)"
            )
        
        # Generate hint
        response = await hint_service.generate_hint(request)
        
        logger.info(f"Hint generated: level {response.level}, cost {response.cost}")
        return response
        
    except ValueError as e:
        # Handle insufficient coins or validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating hint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate hint"
        )


@router.post("/start-monitoring")
async def start_hint_monitoring(
    session: HintTriggerSession,
    hint_service: HintGenerationService = Depends()
):
    """
    Start monitoring student activity for automatic hint triggers
    
    Monitors inactivity and offers hints based on task complexity:
    - Basic tasks: 3 minutes inactivity
    - Intermediate tasks: 5 minutes inactivity  
    - Complex tasks: 8 minutes inactivity
    """
    try:
        await hint_service.start_hint_monitoring(
            student_id=session.student_id,
            task_id=session.task_id,
            task_complexity=session.task_complexity
        )
        
        return {
            "message": "Hint monitoring started",
            "student_id": session.student_id,
            "task_id": session.task_id,
            "monitoring_active": True
        }
        
    except Exception as e:
        logger.error(f"Error starting hint monitoring: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start hint monitoring"
        )


@router.post("/update-activity")
async def update_student_activity(
    student_id: str,
    task_id: str,
    hint_service: HintGenerationService = Depends()
):
    """
    Update student activity to reset inactivity timer
    
    Call this endpoint whenever student makes progress on a task
    to prevent premature hint offers
    """
    try:
        await hint_service.update_activity(student_id, task_id)
        
        return {
            "message": "Activity updated",
            "student_id": student_id,
            "task_id": task_id,
            "timestamp": "now"
        }
        
    except Exception as e:
        logger.error(f"Error updating activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update activity"
        )


@router.post("/stop-monitoring")
async def stop_hint_monitoring(
    student_id: str,
    task_id: str,
    hint_service: HintGenerationService = Depends()
):
    """
    Stop monitoring when task is completed or abandoned
    
    Call this when student completes a task or moves to a different task
    """
    try:
        await hint_service.stop_hint_monitoring(student_id, task_id)
        
        return {
            "message": "Hint monitoring stopped",
            "student_id": student_id,
            "task_id": task_id,
            "monitoring_active": False
        }
        
    except Exception as e:
        logger.error(f"Error stopping hint monitoring: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop hint monitoring"
        )


@router.post("/feedback")
async def submit_hint_feedback(
    hint_id: str,
    student_id: str,
    effectiveness_score: int,
    led_to_solution: bool,
    feedback: Optional[str] = None,
    hint_service: HintGenerationService = Depends()
):
    """
    Submit feedback on hint helpfulness
    
    Helps improve hint generation algorithms and track learning effectiveness
    """
    try:
        # Validate effectiveness score
        if effectiveness_score < 1 or effectiveness_score > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Effectiveness score must be between 1-5"
            )
        
        await hint_service.record_hint_effectiveness(
            hint_id=hint_id,
            student_id=student_id,
            effectiveness_score=effectiveness_score,
            led_to_solution=led_to_solution,
            feedback=feedback
        )
        
        return {
            "message": "Feedback recorded",
            "hint_id": hint_id,
            "effectiveness_score": effectiveness_score,
            "led_to_solution": led_to_solution
        }
        
    except Exception as e:
        logger.error(f"Error submitting hint feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record hint feedback"
        )


@router.get("/history/{student_id}")
async def get_hint_history(
    student_id: str,
    limit: int = 50,
    hint_service: HintGenerationService = Depends()
):
    """
    Get hint usage history for student
    
    Returns comprehensive hint usage statistics and learning analytics
    """
    try:
        stats = await hint_service.get_hint_statistics(student_id)
        
        return {
            "student_id": student_id,
            "hint_statistics": stats,
            "learning_insights": {
                "most_effective_level": stats.get("preferred_hint_level", 2),
                "success_rate": stats.get("success_rate_after_hint", 0.0),
                "total_coins_invested": stats.get("total_coins_spent", 0),
                "learning_progress": "improving" if stats.get("success_rate_after_hint", 0) > 0.7 else "developing"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting hint history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve hint history"
        )


@router.get("/profile/{student_id}", response_model=StudentHintProfile)
async def get_student_hint_profile(
    student_id: str,
    profile_service: StudentProfileService = Depends()
):
    """
    Get student's hint profile including preferences and usage patterns
    
    Returns personalization data used for hint generation optimization
    """
    try:
        profile = await profile_service.get_student_profile(student_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )
        
        # Transform to hint profile format
        hint_profile = StudentHintProfile(
            student_id=student_id,
            coin_balance=profile.performance_metrics.get("coin_balance", 100),
            learning_preferences=profile.preferences,
            concept_mastery=profile.concept_mastery_map,
            error_recovery_pattern=profile.learning_patterns.get("error_recovery_style", "needs-practice"),
            hint_usage_stats=profile.performance_metrics.get("hint_usage_stats", {
                "total_requested": 0,
                "success_after_hint": 0,
                "level_distribution": {"1": 0, "2": 0, "3": 0, "4": 0}
            })
        )
        
        return hint_profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student hint profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve student hint profile"
        )


@router.get("/levels")
async def get_hint_levels():
    """
    Get available hint levels and their descriptions
    
    Returns the four-tier hint system information for UI display
    """
    try:
        levels = {
            1: {
                "name": "Conceptual Guidance",
                "description": "High-level conceptual direction without specific implementation details",
                "cost": 1,
                "example": "This problem requires joining data from multiple tables"
            },
            2: {
                "name": "Directional Hints",
                "description": "Specific direction about which SQL constructs to use",
                "cost": 2,
                "example": "Use INNER JOIN to connect the users and orders tables based on user_id"
            },
            3: {
                "name": "Implementation Hints",
                "description": "Code structure and syntax examples",
                "cost": 3,
                "example": "Try this structure: SELECT u.name, o.total FROM users u INNER JOIN orders o ON u.id = o.user_id"
            },
            4: {
                "name": "Complete Solution",
                "description": "Full SQL statement with detailed explanation",
                "cost": 5,
                "reserved_condition": "Reserved for cases where student has exhausted other options"
            }
        }
        
        return {
            "hint_levels": levels,
            "economy_info": {
                "total_levels": 4,
                "cost_range": "1-5 coins",
                "free_conditions": ["First hint per task", "First hint per day"],
                "acquisition_methods": [
                    "Task completion rewards",
                    "Consecutive learning session bonuses", 
                    "Error correction achievements"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting hint levels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve hint levels"
        ) 