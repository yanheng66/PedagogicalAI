"""
Data models for the 5-step teaching flow.
Defines all data structures used in the teaching process.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Step1Data:
    """Data structure for Step 1: Concept Introduction"""
    stepId: int = 1
    aiExplanation: str = ""
    userUnderstanding: bool = False
    reExplanationCount: int = 0
    responseTimeMs: int = 0


@dataclass
class Step2Data:
    """Data structure for Step 2: Example Prediction (MCQ)"""
    stepId: int = 2
    sqlQuery: str = ""
    options: List[str] = None
    userSelection: str = ""
    predictionAccuracy: bool = False
    mcqAttempts: int = 0
    mcqResponseTimeMs: int = 0
    explanationProvided: Optional[str] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = []


@dataclass
class Step3Data:
    """Data structure for Step 3: Conceptual Assessment"""
    stepId: int = 3
    userQuery: str = ""
    userExplanation: str = ""
    sqlCorrectnessScore: float = 0.0
    explanationDepthScore: float = 0.0
    submissionCount: int = 0
    habitualMisunderstandings: List[str] = None
    assessmentTimeMs: int = 0
    
    def __post_init__(self):
        if self.habitualMisunderstandings is None:
            self.habitualMisunderstandings = []


@dataclass
class Step4Data:
    """Data structure for Step 4: Guided Practice"""
    stepId: int = 4
    problemId: str = ""
    difficultyLevel: int = 1  # 1=Easy, 2=Medium, 3=Hard
    practiceSuccess: bool = False
    retryCount: int = 0
    hintCount: int = 0
    errorTypes: List[str] = None
    practiceTimeMs: int = 0
    
    def __post_init__(self):
        if self.errorTypes is None:
            self.errorTypes = []


@dataclass
class Step5Data:
    """Data structure for Step 5: AI-Generated Reflection Poem"""
    stepId: int = 5
    generatedPoem: str = ""
    poemFeedbackRating: Optional[int] = None  # 1-5 rating
    poemReadTimeMs: int = 0


@dataclass
class ChapterData:
    """Data structure for complete chapter progress"""
    userId: str
    chapterId: str
    steps: Dict[str, Any]  # Contains Step1Data through Step5Data
    masteryLevel: float = 0.0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.steps:
            self.steps = {
                "step1": None,
                "step2": None,
                "step3": None,
                "step4": None,
                "step5": None
            }
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"


@dataclass
class EventLogEntry:
    """Data structure for event logging"""
    userId: int
    stepData: Any  # Can be any StepXData
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"


class TeachingFlowData:
    """Container for all step data in a teaching session"""
    
    def __init__(self):
        self.step1: Optional[Step1Data] = None
        self.step2: Optional[Step2Data] = None
        self.step3: Optional[Step3Data] = None
        self.step4: Optional[Step4Data] = None
        self.step5: Optional[Step5Data] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all step data to dictionary format"""
        return {
            "step1": self.step1.__dict__ if self.step1 else None,
            "step2": self.step2.__dict__ if self.step2 else None,
            "step3": self.step3.__dict__ if self.step3 else None,
            "step4": self.step4.__dict__ if self.step4 else None,
            "step5": self.step5.__dict__ if self.step5 else None
        }
    
    def get_step_data(self, step_number: int) -> Optional[Any]:
        """Get data for a specific step number"""
        step_map = {
            1: self.step1,
            2: self.step2,
            3: self.step3,
            4: self.step4,
            5: self.step5
        }
        return step_map.get(step_number)
    
    def set_step_data(self, step_number: int, data: Any) -> None:
        """Set data for a specific step number"""
        if step_number == 1 and isinstance(data, Step1Data):
            self.step1 = data
        elif step_number == 2 and isinstance(data, Step2Data):
            self.step2 = data
        elif step_number == 3 and isinstance(data, Step3Data):
            self.step3 = data
        elif step_number == 4 and isinstance(data, Step4Data):
            self.step4 = data
        elif step_number == 5 and isinstance(data, Step5Data):
            self.step5 = data
        else:
            raise ValueError(f"Invalid step number or data type for step {step_number}") 