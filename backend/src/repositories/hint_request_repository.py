"""
Hint request repository for hint generation and tracking
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_

from src.models.hint_request import HintRequest
from src.repositories.base_repository import BaseRepository


class HintRequestRepository(BaseRepository[HintRequest]):
    """Repository for hint request operations with technical specification support"""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize hint request repository"""
        super().__init__(db_session, HintRequest)
    
    async def create_hint_request(
        self,
        hint_record: Dict[str, Any]
    ) -> HintRequest:
        """Create new hint request according to technical specification"""
        try:
            hint_request = HintRequest(
                student_id=hint_record["student_id"],
                hint_level=hint_record["hint_level"],
                hint_content=hint_record["hint_content"],
                hint_generation_time_ms=hint_record["hint_generation_time_ms"],
                coins_spent=hint_record["coins_spent"],
                requested_context=hint_record["requested_context"],
                created_at=hint_record.get("timestamp", datetime.now())
            )
            
            result = await self.create(hint_request)
            return result
            
        except Exception as e:
            raise Exception(f"Failed to create hint request: {str(e)}")
    
    async def update_hint_response(
        self,
        request_id: str,
        hint_content: str,
        generation_time_ms: int,
        was_helpful: Optional[bool] = None
    ) -> bool:
        """Update request with generated hint"""
        try:
            update_data = {
                "hint_content": hint_content,
                "hint_generation_time_ms": generation_time_ms,
                "responded_at": datetime.now()
            }
            
            if was_helpful is not None:
                update_data["was_helpful"] = was_helpful
            
            await self.update(request_id, update_data)
            return True
            
        except Exception as e:
            raise Exception(f"Failed to update hint response: {str(e)}")
    
    async def get_student_hint_history(
        self,
        student_id: str,
        limit: int = 50
    ) -> List[HintRequest]:
        """Get hint request history for student"""
        try:
            result = await self.db_session.execute(
                select(HintRequest)
                .where(HintRequest.student_id == student_id)
                .order_by(HintRequest.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
            
        except Exception as e:
            raise Exception(f"Failed to get hint history: {str(e)}")
    
    async def track_hint_effectiveness(
        self,
        request_id: str,
        was_helpful: bool,
        follow_up_success: bool,
        effectiveness_score: Optional[int] = None,
        feedback: Optional[str] = None
    ) -> bool:
        """Track hint effectiveness according to technical specification"""
        try:
            update_data = {
                "was_helpful": was_helpful,
                "led_to_solution": follow_up_success,
                "feedback_submitted_at": datetime.now()
            }
            
            if effectiveness_score is not None:
                update_data["helpfulness_score"] = effectiveness_score
                
            if feedback is not None:
                update_data["student_feedback"] = feedback
            
            await self.update(request_id, update_data)
            return True
            
        except Exception as e:
            raise Exception(f"Failed to track hint effectiveness: {str(e)}")
    
    async def get_hints_for_task(
        self,
        student_id: str,
        task_id: str
    ) -> List[HintRequest]:
        """Get hints for specific task"""
        try:
            # Note: This requires task_id to be stored in requested_context
            result = await self.db_session.execute(
                select(HintRequest)
                .where(
                    and_(
                        HintRequest.student_id == student_id,
                        HintRequest.requested_context.contains({"task_id": task_id})
                    )
                )
                .order_by(HintRequest.created_at.asc())
            )
            return result.scalars().all()
            
        except Exception as e:
            raise Exception(f"Failed to get hints for task: {str(e)}")
    
    async def get_daily_hint_count(
        self,
        student_id: str,
        date: Optional[datetime] = None
    ) -> int:
        """Get number of hints requested by student today"""
        try:
            if date is None:
                date = datetime.now()
                
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            result = await self.db_session.execute(
                select(func.count(HintRequest.id))
                .where(
                    and_(
                        HintRequest.student_id == student_id,
                        HintRequest.created_at >= start_of_day,
                        HintRequest.created_at < end_of_day
                    )
                )
            )
            return result.scalar() or 0
            
        except Exception as e:
            raise Exception(f"Failed to get daily hint count: {str(e)}")
    
    async def get_hint_statistics(
        self,
        student_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive hint statistics for student"""
        try:
            # Total hints by level
            level_stats = await self.db_session.execute(
                select(
                    HintRequest.hint_level,
                    func.count(HintRequest.id).label('count')
                )
                .where(HintRequest.student_id == student_id)
                .group_by(HintRequest.hint_level)
            )
            level_distribution = {str(row.hint_level): row.count for row in level_stats}
            
            # Overall statistics
            overall_stats = await self.db_session.execute(
                select(
                    func.count(HintRequest.id).label('total_hints'),
                    func.sum(HintRequest.coins_spent).label('total_coins'),
                    func.avg(HintRequest.helpfulness_score).label('avg_effectiveness'),
                    func.count(HintRequest.led_to_solution).filter(
                        HintRequest.led_to_solution == True
                    ).label('successful_hints')
                )
                .where(HintRequest.student_id == student_id)
            )
            
            stats = overall_stats.first()
            total_hints = stats.total_hints or 0
            success_rate = (stats.successful_hints or 0) / total_hints if total_hints > 0 else 0.0
            
            return {
                "total_hints_requested": total_hints,
                "hints_by_level": level_distribution,
                "average_effectiveness": float(stats.avg_effectiveness or 0.0),
                "success_rate_after_hint": success_rate,
                "total_coins_spent": int(stats.total_coins or 0),
                "preferred_hint_level": self._calculate_preferred_level(level_distribution)
            }
            
        except Exception as e:
            raise Exception(f"Failed to get hint statistics: {str(e)}")
    
    async def get_error_patterns(
        self,
        student_id: str,
        sql_concept: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get error patterns for student (from hint contexts)"""
        try:
            query = select(HintRequest).where(HintRequest.student_id == student_id)
            
            if sql_concept:
                # Filter by concept in requested_context
                query = query.where(
                    HintRequest.requested_context.contains({"sql_concept": sql_concept})
                )
            
            result = await self.db_session.execute(query)
            hints = result.scalars().all()
            
            # Analyze error patterns from hint contexts
            error_patterns = []
            for hint in hints:
                context = hint.requested_context or {}
                if context.get("error_message"):
                    error_patterns.append({
                        "error_type": self._classify_error(context["error_message"]),
                        "sql_concept": context.get("sql_concept", "unknown"),
                        "frequency": 1,  # Would need aggregation for real frequency
                        "last_occurrence": hint.created_at,
                        "resolution_success_rate": 1.0 if hint.led_to_solution else 0.0
                    })
            
            return error_patterns
            
        except Exception as e:
            raise Exception(f"Failed to get error patterns: {str(e)}")
    
    def _calculate_preferred_level(self, level_distribution: Dict[str, int]) -> int:
        """Calculate student's preferred hint level"""
        if not level_distribution:
            return 2  # Default to level 2
            
        # Find most frequently used level
        max_count = 0
        preferred_level = 2
        
        for level_str, count in level_distribution.items():
            if count > max_count:
                max_count = count
                preferred_level = int(level_str)
        
        return preferred_level
    
    def _classify_error(self, error_message: str) -> str:
        """Classify error type from error message"""
        error_message_lower = error_message.lower()
        
        if "syntax" in error_message_lower:
            return "syntax_error"
        elif "join" in error_message_lower:
            return "join_error"
        elif "column" in error_message_lower:
            return "column_error"
        elif "table" in error_message_lower:
            return "table_error"
        elif "group by" in error_message_lower:
            return "aggregation_error"
        else:
            return "general_error" 