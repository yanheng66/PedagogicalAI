"""
Learning Path Service for adaptive and personalized learning trajectories
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from src.models.concept import Concept
from src.repositories.student_repository import StudentRepository
from src.repositories.concept_repository import ConceptRepository
from src.services.concept_tracker import ConceptTracker
from src.services.student_profile_service import StudentProfileService
from src.schemas.learning import LearningPath, ActivityResult, PathUpdate, PathAdjustment, LearningContext, PerformanceMetrics

logger = logging.getLogger(__name__)


class LearningPathService:
    """
    Service for generating and managing adaptive learning paths.
    Creates personalized learning sequences based on student ability,
    prerequisites, and learning objectives.
    """
    
    def __init__(
        self,
        student_repo: StudentRepository,
        concept_repo: ConceptRepository,
        concept_tracker: ConceptTracker,
        student_profile_service: StudentProfileService
    ):
        """Initialize learning path service with dependencies"""
        self.student_repo = student_repo
        self.concept_repo = concept_repo
        self.concept_tracker = concept_tracker
        self.student_profile_service = student_profile_service
        
        # Path generation parameters
        self.MAX_CONCEPTS_PER_SESSION = 3
        self.MIN_MASTERY_FOR_PROGRESSION = 0.7
        self.LOOKAHEAD_CONCEPTS = 5
        
    async def generate_learning_path(
        self,
        student_id: str,
        target_objectives: List[str]
    ) -> LearningPath:
        """
        Generate personalized learning path based on student state and objectives
        """
        try:
            logger.info(f"Generating learning path for student: {student_id}")
            
            # Get student's current state
            mastery_map = await self.concept_tracker.get_mastery_map(student_id)
            profile = await self.student_profile_service.get_student_profile(student_id)
            
            # Get available concepts and their dependencies
            available_concepts = await self._get_available_concepts()
            
            # Build concept dependency graph
            dependency_graph = await self._build_dependency_graph(available_concepts)
            
            # Find optimal learning sequence
            learning_sequence = await self._calculate_optimal_sequence(
                student_id, mastery_map, target_objectives, dependency_graph
            )
            
            # Generate learning activities for each concept
            activities = await self._generate_learning_activities(
                learning_sequence, profile
            )
            
            # Estimate completion timeline
            estimated_duration = await self._estimate_completion_time(
                learning_sequence, profile
            )
            
            path = LearningPath(
                student_id=student_id,
                path_id=self._generate_path_id(student_id),
                target_objectives=target_objectives,
                concept_sequence=learning_sequence,
                activities=activities,
                estimated_duration_days=estimated_duration,
                difficulty_level=profile.current_difficulty_level if profile else "beginner",
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            logger.info(
                f"Generated path with {len(learning_sequence)} concepts, "
                f"estimated duration: {estimated_duration} days"
            )
            
            return path
            
        except Exception as e:
            logger.error(f"Error generating learning path: {str(e)}")
            raise
    
    async def update_path_progress(
        self,
        student_id: str,
        completed_activity: ActivityResult
    ) -> PathUpdate:
        """
        Update learning path progress based on completed activity
        """
        try:
            logger.info(f"Updating path progress for student: {student_id}")
            
            # Get current path
            current_path = await self._get_current_path(student_id)
            
            # Update concept mastery based on activity result
            await self.concept_tracker.update_mastery_level(
                student_id, 
                completed_activity.concept, 
                completed_activity.performance
            )
            
            # Check if concept is mastered
            mastery_achieved = completed_activity.performance.score >= self.MIN_MASTERY_FOR_PROGRESSION
            
            # Update path progression
            next_concept = None
            path_completed = False
            
            if mastery_achieved:
                next_concept = await self._get_next_concept_in_path(student_id, current_path)
                if not next_concept:
                    path_completed = True
            
            # Check if path needs adjustment
            needs_adjustment = await self._check_if_path_needs_adjustment(
                student_id, completed_activity
            )
            
            update = PathUpdate(
                student_id=student_id,
                completed_concept=completed_activity.concept,
                mastery_achieved=mastery_achieved,
                next_concept=next_concept,
                path_completed=path_completed,
                needs_adjustment=needs_adjustment,
                updated_at=datetime.now()
            )
            
            logger.info(
                f"Path updated: concept {completed_activity.concept} "
                f"{'mastered' if mastery_achieved else 'still learning'}"
            )
            
            return update
            
        except Exception as e:
            logger.error(f"Error updating path progress: {str(e)}")
            raise
    
    async def adapt_path_difficulty(
        self,
        student_id: str,
        performance_metrics: PerformanceMetrics
    ) -> PathAdjustment:
        """
        Adapt learning path difficulty based on student performance
        """
        try:
            logger.info(f"Adapting path difficulty for student: {student_id}")
            
            # Analyze recent performance trends
            performance_trend = await self._analyze_performance_trend(
                student_id, performance_metrics
            )
            
            # Determine if difficulty adjustment is needed
            adjustment_needed = False
            new_difficulty = None
            adjustment_reason = None
            
            current_difficulty = performance_metrics.current_difficulty_level
            
            if performance_trend["struggling"]:
                # Student is struggling - reduce difficulty
                if current_difficulty in ["intermediate", "advanced"]:
                    new_difficulty = self._reduce_difficulty(current_difficulty)
                    adjustment_needed = True
                    adjustment_reason = "Performance indicates need for easier content"
                    
            elif performance_trend["excelling"]:
                # Student is excelling - increase difficulty
                if current_difficulty in ["beginner", "intermediate"]:
                    new_difficulty = self._increase_difficulty(current_difficulty)
                    adjustment_needed = True
                    adjustment_reason = "Performance indicates readiness for harder content"
            
            # Generate new activities if adjustment is needed
            adjusted_activities = []
            if adjustment_needed:
                adjusted_activities = await self._generate_adjusted_activities(
                    student_id, new_difficulty
                )
            
            adjustment = PathAdjustment(
                student_id=student_id,
                adjustment_needed=adjustment_needed,
                old_difficulty=current_difficulty,
                new_difficulty=new_difficulty,
                reason=adjustment_reason,
                performance_indicators=performance_trend,
                adjusted_activities=adjusted_activities,
                adjusted_at=datetime.now()
            )
            
            if adjustment_needed:
                logger.info(
                    f"Difficulty adjusted from {current_difficulty} to {new_difficulty}: "
                    f"{adjustment_reason}"
                )
            
            return adjustment
            
        except Exception as e:
            logger.error(f"Error adapting path difficulty: {str(e)}")
            raise
    
    async def get_recommended_next_steps(self, student_id: str) -> List[Dict[str, Any]]:
        """
        Get recommended next learning steps for student
        """
        try:
            # Get next concepts from concept tracker
            next_concepts = await self.concept_tracker.get_next_concepts(student_id)
            
            # Get current path context
            current_path = await self._get_current_path(student_id)
            
            # Generate specific activity recommendations
            recommendations = []
            
            for concept_info in next_concepts[:3]:  # Top 3 recommendations
                activities = await self._get_concept_activities(
                    concept_info["concept"], student_id
                )
                
                recommendation = {
                    "concept": concept_info["concept"],
                    "reason": concept_info["reason"],
                    "priority": concept_info["priority"],
                    "estimated_time_minutes": concept_info.get("estimated_time", 30),
                    "activities": activities,
                    "prerequisites_met": concept_info["prerequisites_met"]
                }
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting next steps: {str(e)}")
            raise
    
    async def _get_available_concepts(self) -> List[Concept]:
        """Get all available learning concepts"""
        # TODO: Implement concept retrieval from database
        return []
    
    async def _build_dependency_graph(self, concepts: List[Concept]) -> Dict[str, List[str]]:
        """Build concept dependency graph"""
        # TODO: Implement dependency graph construction
        return {}
    
    async def _calculate_optimal_sequence(
        self,
        student_id: str,
        mastery_map: Any,
        objectives: List[str],
        dependency_graph: Dict[str, List[str]]
    ) -> List[str]:
        """Calculate optimal learning sequence using topological sort"""
        # TODO: Implement sequence optimization algorithm
        # - Topological sort respecting dependencies
        # - Consider current mastery levels
        # - Optimize for learning objectives
        # - Apply difficulty progression
        
        # Placeholder sequence
        return ["SELECT", "WHERE", "JOIN", "GROUP BY", "SUBQUERIES"]
    
    async def _generate_learning_activities(
        self,
        concept_sequence: List[str],
        profile: Any
    ) -> List[Dict[str, Any]]:
        """Generate learning activities for concept sequence"""
        # TODO: Implement activity generation
        # - Match activities to learning style
        # - Consider difficulty preferences
        # - Include variety of activity types
        
        activities = []
        for concept in concept_sequence:
            activity = {
                "concept": concept,
                "type": "interactive_exercise",
                "estimated_minutes": 25,
                "difficulty": "beginner"
            }
            activities.append(activity)
        
        return activities
    
    async def _estimate_completion_time(
        self,
        concept_sequence: List[str],
        profile: Any
    ) -> int:
        """Estimate completion time for learning path"""
        # TODO: Implement time estimation
        # - Consider student learning velocity
        # - Factor in concept difficulty
        # - Include practice and review time
        
        # Placeholder: 3 days per concept
        return len(concept_sequence) * 3
    
    def _generate_path_id(self, student_id: str) -> str:
        """Generate unique path ID"""
        timestamp = datetime.now().isoformat()
        import hashlib
        return hashlib.md5(f"{student_id}:{timestamp}".encode()).hexdigest()[:12]
    
    async def _get_current_path(self, student_id: str) -> Optional[LearningPath]:
        """Get student's current learning path"""
        # TODO: Implement path retrieval
        return None
    
    async def _get_next_concept_in_path(
        self,
        student_id: str,
        path: LearningPath
    ) -> Optional[str]:
        """Get next concept in learning path"""
        # TODO: Implement next concept logic
        return None
    
    async def _check_if_path_needs_adjustment(
        self,
        student_id: str,
        activity_result: ActivityResult
    ) -> bool:
        """Check if learning path needs adjustment"""
        # TODO: Implement adjustment detection
        return False
    
    async def _analyze_performance_trend(
        self,
        student_id: str,
        metrics: PerformanceMetrics
    ) -> Dict[str, Any]:
        """Analyze student performance trends"""
        # TODO: Implement trend analysis
        return {"struggling": False, "excelling": False, "stable": True}
    
    def _reduce_difficulty(self, current: str) -> str:
        """Reduce difficulty level"""
        mapping = {"advanced": "intermediate", "intermediate": "beginner"}
        return mapping.get(current, current)
    
    def _increase_difficulty(self, current: str) -> str:
        """Increase difficulty level"""
        mapping = {"beginner": "intermediate", "intermediate": "advanced"}
        return mapping.get(current, current)
    
    async def _generate_adjusted_activities(
        self,
        student_id: str,
        new_difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate activities adjusted for new difficulty level"""
        # TODO: Implement adjusted activity generation
        return []
    
    async def _get_concept_activities(
        self,
        concept: str,
        student_id: str
    ) -> List[Dict[str, Any]]:
        """Get available activities for a concept"""
        # TODO: Implement activity retrieval
        return [
            {"type": "tutorial", "estimated_minutes": 15},
            {"type": "practice", "estimated_minutes": 20},
            {"type": "quiz", "estimated_minutes": 10}
        ] 