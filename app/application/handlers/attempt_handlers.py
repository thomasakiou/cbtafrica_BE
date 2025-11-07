from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.infrastructure.database.models import Attempt, Answer, Question, Test
from app.application.commands.attempt_commands import *
from app.domain.attempts.schemas import AttemptResponse
from app.domain.results.schemas import ResultResponse, AnswerResult

class AttemptHandler:
    def __init__(self, db: Session):
        self.db = db
    
    def start_attempt(self, command: StartAttemptCommand) -> AttemptResponse:
        db_attempt = Attempt(
            user_id=command.user_id,
            test_id=command.attempt_data.test_id,
            status="in_progress"
        )
        self.db.add(db_attempt)
        self.db.commit()
        self.db.refresh(db_attempt)
        return AttemptResponse.model_validate(db_attempt)
    
    def submit_attempt(self, command: SubmitAttemptCommand) -> ResultResponse:
        submission = command.submission
        attempt = self.db.query(Attempt).filter(Attempt.id == submission.attempt_id).first()
        if not attempt:
            raise ValueError("Attempt not found")
        
        if attempt.status != "in_progress":
            raise ValueError("Attempt already completed")
        
        test = self.db.query(Test).filter(Test.id == attempt.test_id).first()
        total_score = 0
        correct_answers = 0
        answer_results = []
        
        for answer_data in submission.answers:
            question = self.db.query(Question).filter(Question.id == answer_data.question_id).first()
            if not question:
                continue
            
            is_correct = answer_data.answer_text.strip().lower() == question.correct_answer.strip().lower()
            marks_obtained = 1 if is_correct else 0
            total_score += marks_obtained
            
            if is_correct:
                correct_answers += 1
            
            db_answer = Answer(
                attempt_id=attempt.id,
                question_id=question.id,
                answer_text=answer_data.answer_text,
                is_correct=is_correct,
                marks_obtained=marks_obtained,
                time_spent=answer_data.time_spent
            )
            self.db.add(db_answer)
            
            answer_results.append(AnswerResult(
                question_id=question.id,
                question_text=question.question_text,
                user_answer=answer_data.answer_text,
                correct_answer=question.correct_answer,
                is_correct=is_correct,
                marks_obtained=marks_obtained,
                total_marks=1,
                explanation=question.explanation
            ))
        
        percentage = (total_score / test.total_marks) * 100 if test.total_marks > 0 else 0
        passed = total_score >= test.passing_marks
        
        attempt.end_time = datetime.utcnow()
        attempt.status = "completed"
        attempt.score = total_score
        attempt.percentage = percentage
        attempt.passed = passed
        
        self.db.commit()
        
        return ResultResponse(
            attempt_id=attempt.id,
            user_id=attempt.user_id,
            test_id=attempt.test_id,
            test_title=test.title,
            start_time=attempt.start_time,
            end_time=attempt.end_time,
            total_questions=len(submission.answers),
            correct_answers=correct_answers,
            score=total_score,
            percentage=percentage,
            passed=passed,
            answers=answer_results
        )
    
    def get_user_attempts(self, command: GetUserAttemptsCommand) -> List[AttemptResponse]:
        attempts = self.db.query(Attempt).filter(Attempt.user_id == command.user_id).all()
        return [AttemptResponse.model_validate(attempt) for attempt in attempts]
    
    def get_attempt_by_id(self, command: GetAttemptCommand) -> AttemptResponse:
        attempt = self.db.query(Attempt).filter(Attempt.id == command.attempt_id).first()
        if not attempt:
            raise ValueError("Attempt not found")
        return AttemptResponse.model_validate(attempt)