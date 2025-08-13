import json
from typing import Dict, Any

from sqlalchemy.orm import Session

from database import get_db_session
from models.db_models import Step3Error, Step4Error


def save_step3_error(
    user_id: str,
    concept: str,
    attempt_data: Dict[str, Any],
    gpt_analysis: Dict[str, Any],
    db: Session | None = None,
) -> int:
    """Persist a Step-3 error (or success) into the database.

    attempt_data keys expected:
        - query:            str
        - attempt_number:   int
        - time_elapsed:     int (seconds)
        - hints_used:       int
    """
    own_session = db is None
    session = db or get_db_session().__enter__()

    record = Step3Error(
        user_id=user_id,
        concept=concept,
        user_query=attempt_data["query"],
        error_analysis=json.dumps(gpt_analysis, ensure_ascii=False),
        attempts=attempt_data["attempt_number"],
        time_spent_seconds=attempt_data["time_elapsed"],
        hints_used=attempt_data.get("hints_used", 0),
        final_success=gpt_analysis.get("is_correct", False),
    )
    session.add(record)

    if own_session:
        session.commit()
        session.close()

    return record.id


def save_step4_error(
    user_id: str,
    concept: str,
    problem_data: Dict[str, Any],
    attempt_data: Dict[str, Any],
    gpt_analysis: Dict[str, Any],
    db: Session | None = None,
) -> int:
    """Persist a Step-4 error (or success) into the database.

    problem_data keys expected:
        - description
        - expected_concepts (list)
        - difficulty

    attempt_data keys expected:
        - solution:        str
        - attempt_number:  int
    """
    own_session = db is None
    session = db or get_db_session().__enter__()

    record = Step4Error(
        user_id=user_id,
        concept=concept,
        problem_description=problem_data["description"],
        included_concepts=json.dumps(problem_data["expected_concepts"], ensure_ascii=False),
        difficulty=problem_data["difficulty"],
        user_solution=attempt_data["solution"],
        error_analysis=json.dumps(gpt_analysis, ensure_ascii=False),
        attempts=attempt_data["attempt_number"],
        final_success=gpt_analysis.get("is_correct", False),
    )
    session.add(record)

    if own_session:
        session.commit()
        session.close()

    return record.id 