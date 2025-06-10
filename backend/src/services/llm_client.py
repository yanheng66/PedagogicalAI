"""
LLM Client for external language model integration
"""

from typing import Dict, Any, Optional
import logging
import asyncio
import aiohttp
from datetime import datetime

from src.config.settings import get_settings
from src.schemas.llm import LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Client for integrating with external LLM services (OpenAI via OpenRouter)
    Handles prompt generation, API calls, response parsing, and error handling
    """
    
    def __init__(self):
        """Initialize LLM client with configuration"""
        self.settings = get_settings()
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.settings.llm_timeout)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def analyze_sql(self, query: str, context: Dict[str, Any]) -> LLMResponse:
        """
        Analyze SQL query using LLM with educational context
        """
        prompt = self._create_sql_analysis_prompt(query, context)
        
        request = LLMRequest(
            prompt=prompt,
            model=self.settings.llm_model,
            temperature=self.settings.llm_temperature,
            max_tokens=self.settings.llm_max_tokens,
            context=context
        )
        
        return await self._make_llm_request(request)
    
    async def generate_hint(self, level: int, context: Dict[str, Any]) -> LLMResponse:
        """
        Generate learning hint at specified level
        """
        prompt = self._create_hint_generation_prompt(level, context)
        
        request = LLMRequest(
            prompt=prompt,
            model=self.settings.llm_model,
            temperature=self.settings.llm_temperature,
            max_tokens=self.settings.llm_max_tokens,
            context=context
        )
        
        return await self._make_llm_request(request)
    
    async def evaluate_prediction(
        self, 
        prediction: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> LLMResponse:
        """
        Evaluate student prediction and provide feedback
        """
        prompt = self._create_prediction_evaluation_prompt(prediction, context)
        
        request = LLMRequest(
            prompt=prompt,
            model=self.settings.llm_model,
            temperature=self.settings.llm_temperature,
            max_tokens=self.settings.llm_max_tokens,
            context=context
        )
        
        return await self._make_llm_request(request)
    
    async def _make_llm_request(self, request: LLMRequest) -> LLMResponse:
        """
        Make HTTP request to LLM API with retry logic and error handling
        """
        if not self.session:
            raise RuntimeError("LLM client session not initialized")
            
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/pedagogical-ai/sql-learning",
            "X-Title": "AI-Driven SQL Learning System"
        }
        
        payload = {
            "model": request.model,
            "messages": [
                {"role": "system", "content": "You are an expert SQL educator and analyzer."},
                {"role": "user", "content": request.prompt}
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
        
        try:
            async with self.session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                return LLMResponse(
                    content=data["choices"][0]["message"]["content"],
                    model=data["model"],
                    usage=data.get("usage", {}),
                    finish_reason=data["choices"][0].get("finish_reason"),
                    created_at=datetime.now(),
                    request_id=data.get("id")
                )
                
        except aiohttp.ClientError as e:
            logger.error(f"LLM API request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in LLM request: {str(e)}")
            raise
    
    def _create_sql_analysis_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """
        Create prompt for SQL analysis with educational context
        """
        # TODO: Implement sophisticated prompt engineering
        # - Include student level and learning context
        # - Structure analysis requirements
        # - Specify output format
        base_prompt = f"""
        Analyze the following SQL query for a student learning SQL:
        
        Query: {query}
        
        Student Context:
        - Level: {context.get('student_level', 'beginner')}
        - Learning Objective: {context.get('learning_objective', 'general SQL practice')}
        
        Please provide:
        1. Syntax validation and errors
        2. Logical correctness assessment
        3. Performance considerations
        4. Educational insights and improvement suggestions
        5. Concepts demonstrated or missing
        
        Format response as structured JSON.
        """
        return base_prompt
    
    def _create_hint_generation_prompt(self, level: int, context: Dict[str, Any]) -> str:
        """
        Create prompt for generating learning hints at specified level
        """
        hint_levels = {
            1: "high-level conceptual guidance",
            2: "directional suggestions", 
            3: "specific implementation hints",
            4: "detailed step-by-step guidance"
        }
        
        prompt = f"""
        Generate a {hint_levels.get(level, 'appropriate')} hint for a student working on:
        
        Problem: {context.get('problem_description', '')}
        Current Query: {context.get('current_query', '')}
        Student Level: {context.get('student_level', 'beginner')}
        
        The hint should be at level {level} (1=conceptual, 4=detailed).
        Focus on guiding learning rather than giving direct answers.
        """
        return prompt
    
    def _create_prediction_evaluation_prompt(
        self, 
        prediction: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> str:
        """
        Create prompt for evaluating student predictions
        """
        prompt = f"""
        Evaluate a student's prediction about SQL query results:
        
        Query: {context.get('query', '')}
        Student Prediction: {prediction}
        Actual Result: {context.get('actual_result', '')}
        
        Assess:
        1. Accuracy of prediction
        2. Understanding demonstrated
        3. Common misconceptions revealed
        4. Constructive feedback for improvement
        
        Provide encouraging, educational feedback.
        """
        return prompt 