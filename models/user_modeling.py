"""
User modeling system for the 5-step dynamic teaching flow.
Includes StepInfoRetrieve and UserModel according to the design document.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .teaching_flow_data import ChapterData


@dataclass
class StepInfoRetrieve:
    """
    Aggregate summary for long-term historical data analysis.
    Supports metacognitive feedback and intelligent recommendations.
    """
    totalAttempts: int = 0
    totalErrors: int = 0
    avgDurationSec: float = 0.0
    avgAccuracy: float = 0.0
    avgDepthScore: Optional[float] = None  # For Step3 only
    avgHintCount: Optional[float] = None   # For Step4 only
    commonMisunderstandings: List[str] = field(default_factory=list)
    commonErrorTypes: List[str] = field(default_factory=list)
    retentionTrend: List[float] = field(default_factory=list)  # Time series performance data
    
    def update_from_step_data(self, step_data: any, step_number: int) -> None:
        """Update aggregate statistics from new step data"""
        if step_number == 3 and hasattr(step_data, 'sqlCorrectnessScore'):
            # Update Step3 specific metrics
            self.totalAttempts += step_data.submissionCount
            self.totalErrors += len(step_data.habitualMisunderstandings)
            
            # Update averages
            if self.totalAttempts > 0:
                self.avgAccuracy = (self.totalAttempts - self.totalErrors) / self.totalAttempts
            
            # Update duration
            duration_sec = step_data.assessmentTimeMs / 1000.0
            if self.avgDurationSec == 0:
                self.avgDurationSec = duration_sec
            else:
                self.avgDurationSec = (self.avgDurationSec + duration_sec) / 2
            
            # Update depth score
            if self.avgDepthScore is None:
                self.avgDepthScore = step_data.explanationDepthScore
            else:
                self.avgDepthScore = (self.avgDepthScore + step_data.explanationDepthScore) / 2
            
            # Add misunderstandings
            for misunderstanding in step_data.habitualMisunderstandings:
                if misunderstanding not in self.commonMisunderstandings:
                    self.commonMisunderstandings.append(misunderstanding)
        
        elif step_number == 4 and hasattr(step_data, 'practiceSuccess'):
            # Update Step4 specific metrics
            self.totalAttempts += step_data.retryCount
            if not step_data.practiceSuccess:
                self.totalErrors += 1
            
            # Update averages
            if self.totalAttempts > 0:
                self.avgAccuracy = (self.totalAttempts - self.totalErrors) / self.totalAttempts
            
            # Update duration
            duration_sec = step_data.practiceTimeMs / 1000.0
            if self.avgDurationSec == 0:
                self.avgDurationSec = duration_sec
            else:
                self.avgDurationSec = (self.avgDurationSec + duration_sec) / 2
            
            # Update hint count
            if self.avgHintCount is None:
                self.avgHintCount = float(step_data.hintCount)
            else:
                self.avgHintCount = (self.avgHintCount + step_data.hintCount) / 2
            
            # Add error types
            for error_type in step_data.errorTypes:
                if error_type not in self.commonErrorTypes:
                    self.commonErrorTypes.append(error_type)


@dataclass
class UserModel:
    """
    Comprehensive user model for the 5-step teaching system.
    Contains learning progress and aggregate statistics.
    """
    userId: str
    name: str
    learningProgress: List[ChapterData] = field(default_factory=list)
    step3InfoRetrieve: StepInfoRetrieve = field(default_factory=StepInfoRetrieve)
    step4InfoRetrieve: StepInfoRetrieve = field(default_factory=StepInfoRetrieve)
    
    def add_chapter_data(self, chapter_data: ChapterData) -> None:
        """Add completed chapter data and update aggregate statistics"""
        # Add to learning progress
        self.learningProgress.append(chapter_data)
        
        # Update Step3 and Step4 aggregate data
        if chapter_data.steps.get("step3"):
            self.step3InfoRetrieve.update_from_step_data(
                chapter_data.steps["step3"], 3
            )
        
        if chapter_data.steps.get("step4"):
            self.step4InfoRetrieve.update_from_step_data(
                chapter_data.steps["step4"], 4
            )
    
    def get_overall_mastery_level(self) -> float:
        """Calculate overall mastery level across all chapters"""
        if not self.learningProgress:
            return 0.0
        
        total_mastery = sum(chapter.masteryLevel for chapter in self.learningProgress)
        return total_mastery / len(self.learningProgress)
    
    def get_recent_performance(self, last_n_chapters: int = 3) -> float:
        """Get average performance for the last N chapters"""
        if not self.learningProgress:
            return 0.0
        
        recent_chapters = self.learningProgress[-last_n_chapters:]
        total_mastery = sum(chapter.masteryLevel for chapter in recent_chapters)
        return total_mastery / len(recent_chapters)
    
    def get_concept_progress(self) -> List[str]:
        """Get list of concepts the user has worked on"""
        concepts = []
        for chapter in self.learningProgress:
            concepts.append(chapter.chapterId)
        return concepts
    
    def get_strength_areas(self) -> List[str]:
        """Identify areas where the user performs well"""
        strengths = []
        
        # High accuracy in Step3
        if self.step3InfoRetrieve.avgAccuracy > 0.8:
            strengths.append("SQL Query Writing")
        
        if self.step3InfoRetrieve.avgDepthScore and self.step3InfoRetrieve.avgDepthScore > 0.8:
            strengths.append("Concept Explanation")
        
        # Low hint usage in Step4
        if self.step4InfoRetrieve.avgHintCount and self.step4InfoRetrieve.avgHintCount < 2:
            strengths.append("Problem Solving")
        
        return strengths
    
    def get_focus_areas(self) -> List[str]:
        """Identify areas that need improvement"""
        focus_areas = []
        
        # Common misunderstandings from Step3
        if len(self.step3InfoRetrieve.commonMisunderstandings) > 3:
            focus_areas.append("Conceptual Understanding")
        
        # High error rate
        if self.step3InfoRetrieve.avgAccuracy < 0.6:
            focus_areas.append("SQL Syntax and Logic")
        
        # High hint usage in Step4
        if self.step4InfoRetrieve.avgHintCount and self.step4InfoRetrieve.avgHintCount > 3:
            focus_areas.append("Independent Problem Solving")
        
        return focus_areas 