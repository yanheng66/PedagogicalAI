"""
Hint Generation Service for multi-level intelligent learning hints
"""

import logging
from typing import Dict, Any, Optional, List
import hashlib
from datetime import datetime, timedelta
import asyncio

from src.services.llm_client import LLMClient
from src.services.student_profile_service import StudentProfileService
from src.services.concept_tracker import ConceptTracker
from src.services.cache_service import CacheService
from src.services.coin_management_service import CoinManagementService
from src.schemas.learning import HintRequest, HintResponse, HintContext, LearningActivity, PerformanceMetrics
from src.repositories.hint_request_repository import HintRequestRepository
from src.utils.learning_analytics import LearningAnalytics

logger = logging.getLogger(__name__)


class HintGenerationService:
    """
    Service for generating multi-level intelligent hints with automated triggers.
    Provides progressive disclosure from conceptual guidance to detailed solutions.
    Integrates with coin economy and enforces learned concept boundaries.
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        student_profile_service: StudentProfileService,
        concept_tracker: ConceptTracker,
        cache_service: CacheService,
        coin_management_service: CoinManagementService,
        hint_request_repo: HintRequestRepository,
        learning_analytics: LearningAnalytics
    ):
        """Initialize hint generation service with dependencies"""
        self.llm_client = llm_client
        self.student_profile_service = student_profile_service
        self.concept_tracker = concept_tracker
        self.cache_service = cache_service
        self.coin_management_service = coin_management_service
        self.hint_request_repo = hint_request_repo
        self.learning_analytics = learning_analytics
        
        # Hint level definitions according to technical specification
        self.HINT_LEVELS = {
            1: {
                "name": "Conceptual Guidance",
                "description": "High-level conceptual direction without specific implementation details",
                "detail_level": "minimal",
                "cost": 1,
                "example": "This problem requires joining data from multiple tables"
            },
            2: {
                "name": "Directional Hints", 
                "description": "Specific direction about which SQL constructs to use",
                "detail_level": "moderate",
                "cost": 2,
                "example": "Use INNER JOIN to connect the users and orders tables based on user_id"
            },
            3: {
                "name": "Implementation Hints",
                "description": "Code structure and syntax examples",
                "detail_level": "detailed",
                "cost": 3,
                "example": "Try this structure: SELECT u.name, o.total FROM users u INNER JOIN orders o ON u.id = o.user_id"
            },
            4: {
                "name": "Complete Solution",
                "description": "Full SQL statement with detailed explanation",
                "detail_level": "complete",
                "cost": 5,
                "reserved_condition": "student has exhausted other options"
            }
        }
        
        # Automatic trigger thresholds based on task complexity
        self.TRIGGER_THRESHOLDS = {
            "basic": 3 * 60,      # 3 minutes of inactivity
            "intermediate": 5 * 60,  # 5 minutes of inactivity
            "complex": 8 * 60     # 8 minutes of inactivity
        }
        
        # Active monitoring sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def start_hint_monitoring(
        self, 
        student_id: str, 
        task_id: str, 
        task_complexity: str = "intermediate"
    ) -> None:
        """
        Start monitoring student activity for automatic hint triggers
        """
        try:
            session_key = f"{student_id}_{task_id}"
            
            self.active_sessions[session_key] = {
                "student_id": student_id,
                "task_id": task_id,
                "task_complexity": task_complexity,
                "start_time": datetime.now(),
                "last_activity": datetime.now(),
                "hint_offered": False,
                "hint_declined_count": 0
            }
            
            # Start background monitoring task
            asyncio.create_task(self._monitor_session(session_key))
            
            logger.info(f"Started hint monitoring for student {student_id}, task {task_id}")
            
        except Exception as e:
            logger.error(f"Error starting hint monitoring: {str(e)}")
    
    async def update_activity(self, student_id: str, task_id: str) -> None:
        """
        Update student activity timestamp to reset inactivity timer
        """
        session_key = f"{student_id}_{task_id}"
        if session_key in self.active_sessions:
            self.active_sessions[session_key]["last_activity"] = datetime.now()
            self.active_sessions[session_key]["hint_offered"] = False
    
    async def stop_hint_monitoring(self, student_id: str, task_id: str) -> None:
        """
        Stop monitoring when task is completed or abandoned
        """
        session_key = f"{student_id}_{task_id}"
        if session_key in self.active_sessions:
            del self.active_sessions[session_key]
            logger.info(f"Stopped hint monitoring for student {student_id}, task {task_id}")

    async def _monitor_session(self, session_key: str) -> None:
        """
        Background task to monitor session for hint trigger conditions
        """
        try:
            while session_key in self.active_sessions:
                session = self.active_sessions[session_key]
                current_time = datetime.now()
                
                # Check inactivity duration
                inactivity_duration = (current_time - session["last_activity"]).total_seconds()
                threshold = self.TRIGGER_THRESHOLDS[session["task_complexity"]]
                
                # Trigger hint offer if threshold exceeded and not already offered
                if (inactivity_duration >= threshold and 
                    not session["hint_offered"] and 
                    session["hint_declined_count"] < 3):  # Max 3 automatic offers
                    
                    await self._trigger_hint_offer(session)
                    session["hint_offered"] = True
                
                # Sleep before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            logger.error(f"Error in session monitoring: {str(e)}")
    
    async def _trigger_hint_offer(self, session: Dict[str, Any]) -> None:
        """
        Trigger non-intrusive hint offer to student
        """
        try:
            student_id = session["student_id"]
            task_id = session["task_id"]
            
            # Check coin balance before offering
            balance = await self.coin_management_service.get_balance(student_id)
            
            # Get student's preferred hint level for cost estimation
            profile = await self.student_profile_service.get_student_profile(student_id)
            preferred_level = profile.learning_preferences.get("preferred_hint_level", 2) if profile else 2
            hint_cost = self.HINT_LEVELS[preferred_level]["cost"]
            
            if balance >= hint_cost:
                # Send hint offer notification (would integrate with notification system)
                logger.info(
                    f"Triggering hint offer for student {student_id}, task {task_id}, "
                    f"cost: {hint_cost} coins, balance: {balance}"
                )
                
                # TODO: Integrate with notification/UI system to show "Need some help?" prompt
                
            else:
                logger.debug(f"Insufficient balance for hint offer: {balance} < {hint_cost}")
                
        except Exception as e:
            logger.error(f"Error triggering hint offer: {str(e)}")
    
    async def generate_hint(self, request: HintRequest) -> HintResponse:
        """
        Generate intelligent hint based on student context and request level
        """
        try:
            start_time = datetime.now()
            
            # Validate coin balance before processing
            await self._validate_coin_balance(request.student_id, request.level)
            
            # Enforce learned concept boundaries
            available_concepts = await self._get_available_concepts(
                request.student_id, request.context
            )
            
            # Check cache first
            cache_key = self._generate_hint_cache_key(request)
            cached_hint = await self.cache_service.get_hint_cache(cache_key)
            
            if cached_hint:
                logger.debug(f"Retrieved hint from cache: {cache_key}")
                return await self._create_hint_response(
                    request, cached_hint, start_time, cached=True
                )
            
            # Determine optimal hint level if not specified
            if request.level == 0:  # Auto-determine level
                optimal_level = await self._calculate_optimal_hint_level(
                    request.student_id, request.context
                )
                request.level = optimal_level
            
            # Generate contextual hint with concept boundary enforcement
            hint_content = await self._generate_contextual_hint_with_boundaries(
                request.level, request.context, available_concepts
            )
            
            # Cache the hint
            await self.cache_service.set_hint_cache(cache_key, hint_content)
            
            # Process coin payment
            await self._process_hint_payment(request.student_id, request.level, request.context)
            
            # Create and store hint request record
            hint_record = await self._create_hint_record(request, hint_content, start_time)
            
            response = await self._create_hint_response(
                request, hint_content, start_time, cached=False, hint_record=hint_record
            )
            
            logger.info(
                f"Generated level {request.level} hint for student: {request.student_id}, "
                f"cost: {response.cost}, time: {response.generation_time_ms}ms"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating hint: {str(e)}")
            raise
    
    async def _validate_coin_balance(self, student_id: str, hint_level: int) -> None:
        """
        Validate student has sufficient coins for hint request
        """
        try:
            current_balance = await self.coin_management_service.get_balance(student_id)
            required_cost = self.HINT_LEVELS[hint_level]["cost"]
            
            if current_balance < required_cost:
                raise ValueError(
                    f"Insufficient coins: {current_balance} < {required_cost} required for level {hint_level} hint"
                )
                
        except Exception as e:
            logger.error(f"Error validating coin balance: {str(e)}")
            raise
    
    async def _get_available_concepts(
        self, 
        student_id: str, 
        context: HintContext
    ) -> List[str]:
        """
        Get concepts available to student based on completed learning modules
        """
        try:
            # Get student's learning progress
            profile = await self.student_profile_service.get_student_profile(student_id)
            
            if not profile:
                return []
            
            # Get completed chapters/modules
            completed_modules = profile.learning_progress.get("completed_modules", [])
            
            # Extract available concepts from completed modules
            available_concepts = []
            for module in completed_modules:
                # TODO: Implement concept extraction from learning modules
                # This would map modules to their constituent SQL concepts
                module_concepts = await self._get_concepts_from_module(module)
                available_concepts.extend(module_concepts)
            
            # Add basic concepts for all students
            basic_concepts = ["SELECT", "FROM", "WHERE", "basic_syntax"]
            available_concepts.extend(basic_concepts)
            
            # Remove duplicates
            return list(set(available_concepts))
            
        except Exception as e:
            logger.error(f"Error getting available concepts: {str(e)}")
            return []
    
    async def _get_concepts_from_module(self, module_name: str) -> List[str]:
        """
        Get SQL concepts taught in a specific learning module
        """
        # TODO: Implement module-to-concept mapping
        # This would be based on curriculum design
        module_concept_map = {
            "basic_queries": ["SELECT", "FROM", "WHERE", "DISTINCT"],
            "joins": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN"],
            "aggregation": ["GROUP BY", "HAVING", "COUNT", "SUM", "AVG", "MAX", "MIN"],
            "subqueries": ["subquery", "EXISTS", "IN", "correlated_subquery"],
            "advanced": ["WINDOW functions", "CTE", "UNION", "INTERSECT", "EXCEPT"]
        }
        
        return module_concept_map.get(module_name, [])
    
    async def _calculate_optimal_hint_level(
        self,
        student_id: str,
        context: HintContext
    ) -> int:
        """
        Calculate optimal hint level based on student profile and context
        """
        try:
            # Get student profile for personalization
            profile = await self.student_profile_service.get_student_profile(student_id)
            
            # Get concept mastery for current concepts
            mastery_map = await self.concept_tracker.get_mastery_map(student_id)
            
            # TODO: Implement intelligent level calculation
            # - Consider student's preferred hint level
            # - Analyze current struggle level from context
            # - Factor in concept mastery levels
            # - Consider recent hint effectiveness
            # - Apply adaptive learning principles
            
            logger.debug(f"Calculating optimal hint level for student: {student_id}")
            
            # Placeholder calculation logic
            base_level = 2  # Start with directional suggestions
            
            # Adjust based on student preferences
            if profile and profile.preferences.get("hint_preference") == "minimal":
                base_level = max(1, base_level - 1)
            elif profile and profile.preferences.get("hint_preference") == "detailed":
                base_level = min(4, base_level + 1)
            
            # Adjust based on struggle indicators
            if context.attempts_count > 3:
                base_level = min(4, base_level + 1)
            
            # Adjust based on concept mastery
            relevant_concepts = context.relevant_concepts or []
            if relevant_concepts:
                avg_mastery = sum(
                    mastery_map.concept_scores.get(concept, {}).get("mastery", 0.0)
                    for concept in relevant_concepts
                ) / len(relevant_concepts)
                
                if avg_mastery < 0.3:  # Low mastery
                    base_level = min(4, base_level + 1)
                elif avg_mastery > 0.8:  # High mastery
                    base_level = max(1, base_level - 1)
            
            return base_level
            
        except Exception as e:
            logger.error(f"Error calculating optimal hint level: {str(e)}")
            return 2  # Default to level 2
    
    async def _generate_contextual_hint_with_boundaries(
        self,
        level: int,
        context: HintContext,
        available_concepts: List[str]
    ) -> str:
        """
        Generate contextual hint content with concept boundary enforcement
        """
        try:
            # Build context for LLM prompt with concept boundaries
            llm_context = {
                "problem_description": context.problem_description,
                "current_query": context.current_query,
                "error_message": context.error_message,
                "student_level": context.student_level,
                "available_concepts": available_concepts,  # Enforce boundaries
                "database_schema": context.database_schema,
                "hint_level": level,
                "hint_level_description": self.HINT_LEVELS[level]["description"],
                "constraint": "ONLY use concepts from available_concepts list"
            }
            
            # Generate personalized prompt based on level
            prompt = await self._build_personalized_prompt(level, llm_context)
            
            # Generate hint using LLM with concept constraints
            llm_hint = await self.llm_client.generate_hint(prompt, llm_context)
            
            # Validate and enhance hint content
            enhanced_hint = await self._enhance_hint_with_validation(
                llm_hint, level, context, available_concepts
            )
            
            return enhanced_hint
            
        except Exception as e:
            logger.error(f"Error generating contextual hint: {str(e)}")
            # Return fallback hint that respects concept boundaries
            return await self._generate_boundary_safe_fallback_hint(level, context, available_concepts)
    
    async def _build_personalized_prompt(self, level: int, context: Dict[str, Any]) -> str:
        """
        Build personalized LLM prompt based on hint level and context
        """
        level_info = self.HINT_LEVELS[level]
        
        base_prompt = f"""
        You are an intelligent SQL tutor providing a {level_info['name']} hint.
        
        Level Description: {level_info['description']}
        Detail Level: {level_info['detail_level']}
        
        Student Context:
        - Problem: {context.get('problem_description', 'N/A')}
        - Current Query: {context.get('current_query', 'N/A')}
        - Error: {context.get('error_message', 'N/A')}
        - Available Concepts: {', '.join(context.get('available_concepts', []))}
        
        CRITICAL CONSTRAINT: Only reference SQL concepts from the Available Concepts list.
        Do not introduce concepts the student hasn't learned yet.
        
        """
        
        if level == 1:
            base_prompt += """
            Provide high-level conceptual guidance without specific SQL syntax.
            Focus on the approach and thinking process.
            """
        elif level == 2:
            base_prompt += """
            Provide specific direction about which SQL constructs to use.
            Be more specific than conceptual but don't give full implementation.
            """
        elif level == 3:
            base_prompt += """
            Include code structure and syntax examples.
            Show partial implementation but let student complete it.
            """
        elif level == 4:
            base_prompt += """
            Provide complete solution with detailed explanation.
            Include full SQL statement and explain each part.
            """
        
        return base_prompt
    
    async def _enhance_hint_with_validation(
        self,
        llm_hint: str,
        level: int,
        context: HintContext,
        available_concepts: List[str]
    ) -> str:
        """
        Enhance and validate hint content against concept boundaries
        """
        try:
            # Validate that hint doesn't use unavailable concepts
            if await self._validate_concept_boundaries(llm_hint, available_concepts):
                enhanced_hint = await self._enhance_hint_content(llm_hint, level, context)
                return enhanced_hint
            else:
                # Regenerate with stricter constraints
                logger.warning("Hint violated concept boundaries, regenerating...")
                return await self._regenerate_with_strict_boundaries(
                    level, context, available_concepts
                )
                
        except Exception as e:
            logger.error(f"Error enhancing hint: {str(e)}")
            return llm_hint  # Return original if enhancement fails
    
    async def _validate_concept_boundaries(
        self, 
        hint_content: str, 
        available_concepts: List[str]
    ) -> bool:
        """
        Validate that hint content only uses available concepts
        """
        try:
            # TODO: Implement sophisticated concept detection in hint text
            # This could use NLP to identify SQL concepts mentioned in the hint
            
            hint_upper = hint_content.upper()
            
            # Define concepts that might be mentioned but not available
            all_sql_concepts = [
                "WINDOW", "PARTITION", "RANK", "ROW_NUMBER", "LAG", "LEAD",
                "CTE", "WITH", "RECURSIVE", "LATERAL", "PIVOT", "UNPIVOT",
                "MERGE", "UPSERT", "RETURNING"
            ]
            
            available_concepts_upper = [concept.upper() for concept in available_concepts]
            
            # Check if hint mentions unavailable advanced concepts
            for concept in all_sql_concepts:
                if concept in hint_upper and concept not in available_concepts_upper:
                    logger.warning(f"Hint mentions unavailable concept: {concept}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating concept boundaries: {str(e)}")
            return True  # Default to allowing if validation fails
    
    async def _process_hint_payment(
        self, 
        student_id: str, 
        hint_level: int, 
        context: HintContext
    ) -> None:
        """
        Process coin payment for hint request
        """
        try:
            cost = self.HINT_LEVELS[hint_level]["cost"]
            
            # Check if this is a free hint (first hint or special conditions)
            is_free = await self._check_free_hint_eligibility(student_id, context)
            
            if not is_free:
                await self.coin_management_service.spend_coins(
                    student_id=student_id,
                    service=f"hint_level_{hint_level}",
                    amount=cost,
                    context={
                        "hint_level": hint_level,
                        "task_id": context.task_id if hasattr(context, 'task_id') else None,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            logger.info(f"Processed hint payment: student {student_id}, cost {cost}, free: {is_free}")
            
        except Exception as e:
            logger.error(f"Error processing hint payment: {str(e)}")
            raise
    
    async def _check_free_hint_eligibility(
        self, 
        student_id: str, 
        context: HintContext
    ) -> bool:
        """
        Check if student is eligible for free hint
        """
        try:
            # Check if this is student's first hint for this task
            if hasattr(context, 'task_id'):
                previous_hints = await self.hint_request_repo.get_hints_for_task(
                    student_id, context.task_id
                )
                if not previous_hints:
                    return True  # First hint is free
            
            # Check daily free hint allowance
            today_hints = await self.hint_request_repo.get_daily_hint_count(student_id)
            if today_hints == 0:
                return True  # First hint of the day is free
            
            # Other free hint conditions could be added here
            # - New student grace period
            # - Achievement rewards
            # - Special events
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking free hint eligibility: {str(e)}")
            return False
    
    async def _enhance_hint_content(
        self,
        llm_hint: str,
        level: int,
        context: HintContext
    ) -> str:
        """
        Enhance LLM-generated hint with additional context and formatting
        """
        try:
            level_info = self.HINT_LEVELS[level]
            
            # Add level-specific framing
            if level == 1:
                enhanced = f"💡 **{level_info['name']}**\n\n{llm_hint}"
            elif level == 2:
                enhanced = f"🎯 **{level_info['name']}**\n\n{llm_hint}"
            elif level == 3:
                enhanced = f"⚙️ **{level_info['name']}**\n\n{llm_hint}"
            else:  # level == 4
                enhanced = f"✅ **{level_info['name']}**\n\n{llm_hint}"
            
            # Add context-specific enhancements
            if hasattr(context, 'relevant_concepts') and context.relevant_concepts:
                concepts_text = ", ".join(context.relevant_concepts)
                enhanced += f"\n\n*Related concepts: {concepts_text}*"
            
            if hasattr(context, 'error_message') and context.error_message:
                enhanced += f"\n\n*This hint addresses the error you encountered.*"
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing hint content: {str(e)}")
            return llm_hint
    
    def _generate_fallback_hint(self, level: int, context: HintContext) -> str:
        """
        Generate fallback hint when LLM is unavailable
        """
        level_info = self.HINT_LEVELS[level]
        
        fallback_hints = {
            1: "Think about what SQL concepts might be needed for this problem. Consider the data relationships and what result you want to achieve.",
            2: "Consider breaking this problem into smaller steps. What tables do you need? What conditions should you apply?",
            3: "Look at your current query structure. Check your JOIN conditions and WHERE clauses for correctness.",
            4: "Here's a step-by-step approach: 1) Identify required tables, 2) Determine JOIN conditions, 3) Add WHERE filters, 4) Select appropriate columns."
        }
        
        hint_content = fallback_hints.get(level, "Consider reviewing the relevant SQL concepts and try a different approach.")
        
        return f"**{level_info['name']} (Level {level})**\n\n{hint_content}\n\n*This is a fallback hint. For better personalized guidance, please try again.*"
    
    def _generate_hint_cache_key(self, request: HintRequest) -> str:
        """Generate cache key for hint request"""
        key_data = f"{request.level}:{request.context.problem_description}:{request.context.current_query}:{request.context.student_level}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _generate_hint_id(self, request: HintRequest) -> str:
        """Generate unique hint ID for tracking"""
        timestamp = datetime.now().isoformat()
        id_data = f"{request.student_id}:{request.level}:{timestamp}"
        return hashlib.sha256(id_data.encode()).hexdigest()[:16]
    
    async def record_hint_effectiveness(
        self,
        hint_id: str,
        student_id: str,
        effectiveness_score: int,
        led_to_solution: bool,
        feedback: Optional[str] = None
    ) -> None:
        """
        Record hint effectiveness for improvement and analytics
        """
        try:
            # TODO: Implement effectiveness tracking
            # - Store effectiveness data in database
            # - Update hint generation algorithms
            # - Analyze patterns for improvement
            # - Update student learning preferences
            
            logger.info(
                f"Recorded hint effectiveness: hint_id={hint_id}, "
                f"student={student_id}, score={effectiveness_score}, "
                f"solved={led_to_solution}"
            )
            
        except Exception as e:
            logger.error(f"Error recording hint effectiveness: {str(e)}")
            raise
    
    async def get_hint_statistics(self, student_id: str) -> Dict[str, Any]:
        """
        Get hint usage statistics for a student
        """
        try:
            # TODO: Implement statistics retrieval
            # - Total hints requested by level
            # - Effectiveness rates
            # - Most helpful hint types
            # - Learning progression indicators
            
            # Placeholder statistics
            stats = {
                "total_hints_requested": 45,
                "hints_by_level": {
                    "1": 12,
                    "2": 18,
                    "3": 10,
                    "4": 5
                },
                "average_effectiveness": 3.4,
                "success_rate_after_hint": 0.78,
                "preferred_hint_level": 2,
                "total_coins_spent": 97
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting hint statistics: {str(e)}")
            raise
    
    async def _regenerate_with_strict_boundaries(
        self,
        level: int,
        context: HintContext,
        available_concepts: List[str]
    ) -> str:
        """
        Regenerate hint with stricter concept boundary constraints
        """
        try:
            strict_prompt = f"""
            Generate a level {level} SQL hint using ONLY these concepts: {', '.join(available_concepts)}
            
            STRICT RULES:
            1. Do not mention any SQL concept not in the list above
            2. If the problem requires unavailable concepts, explain conceptually without naming them
            3. Focus on what the student CAN do with available concepts
            
            Problem: {context.problem_description}
            Current Query: {context.current_query}
            Error: {context.error_message}
            """
            
            llm_context = {"strict_mode": True, "available_concepts": available_concepts}
            regenerated_hint = await self.llm_client.generate_hint(strict_prompt, llm_context)
            
            return regenerated_hint
            
        except Exception as e:
            logger.error(f"Error regenerating with strict boundaries: {str(e)}")
            return await self._generate_boundary_safe_fallback_hint(level, context, available_concepts)
    
    async def _generate_boundary_safe_fallback_hint(
        self, 
        level: int, 
        context: HintContext, 
        available_concepts: List[str]
    ) -> str:
        """
        Generate safe fallback hint that respects concept boundaries
        """
        try:
            level_info = self.HINT_LEVELS[level]
            
            if level == 1:
                return "💡 Think about the problem step by step. What is the main goal of this query? Break it down into smaller parts."
            elif level == 2:
                basic_concepts = [c for c in available_concepts if c.upper() in ["SELECT", "FROM", "WHERE", "JOIN"]]
                if basic_concepts:
                    return f"🎯 Consider using these SQL concepts: {', '.join(basic_concepts[:3])}. Focus on how they might help solve your problem."
                else:
                    return "🎯 Review the basic SQL structure and think about what clauses you need for this query."
            elif level == 3:
                return "⚙️ Try building your query step by step: 1) Start with SELECT and FROM, 2) Add WHERE conditions, 3) Include any needed JOINs."
            else:  # level == 4
                return "✅ I'd like to help with the complete solution, but let's work with the concepts you've learned so far. Try the previous hint levels first."
                
        except Exception as e:
            logger.error(f"Error generating fallback hint: {str(e)}")
            return "I'm having trouble generating a hint right now. Please try again or ask for help from your instructor."
    
    async def _create_hint_record(
        self,
        request: HintRequest,
        hint_content: str,
        start_time: datetime
    ) -> Any:
        """
        Create and store hint request record in database
        """
        try:
            generation_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            hint_record = {
                "student_id": request.student_id,
                "hint_level": request.level,
                "hint_content": hint_content,
                "hint_generation_time_ms": generation_time,
                "coins_spent": self.HINT_LEVELS[request.level]["cost"],
                "requested_context": request.context.dict() if request.context else {},
                "timestamp": datetime.now()
            }
            
            # Store in database through repository
            stored_record = await self.hint_request_repo.create_hint_request(hint_record)
            
            return stored_record
            
        except Exception as e:
            logger.error(f"Error creating hint record: {str(e)}")
            return None
    
    async def _create_hint_response(
        self,
        request: HintRequest,
        hint_content: str,
        start_time: datetime,
        cached: bool = False,
        hint_record: Any = None
    ) -> HintResponse:
        """
        Create standardized hint response object
        """
        try:
            generation_time = int((datetime.now() - start_time).total_seconds() * 1000)
            cost = self.HINT_LEVELS[request.level]["cost"]
            
            # Check if this was a free hint
            is_free = await self._check_free_hint_eligibility(request.student_id, request.context)
            
            return HintResponse(
                hint_content=hint_content,
                level=request.level,
                cost=0 if is_free else cost,
                generation_time_ms=generation_time,
                cached=cached,
                hint_id=self._generate_hint_id(request),
                is_free=is_free,
                level_description=self.HINT_LEVELS[request.level]["description"],
                available_levels=list(self.HINT_LEVELS.keys()),
                record_id=hint_record.id if hint_record else None
            )
            
        except Exception as e:
            logger.error(f"Error creating hint response: {str(e)}")
            raise