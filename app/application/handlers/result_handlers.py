from sqlalchemy.orm import Session
from app.infrastructure.database.models import Attempt, Test, Answer, Question
from app.application.commands.result_commands import *
from app.domain.results.schemas import ResultResponse, ResultSummary, AnswerResult
from typing import List

class ResultHandler:
    def __init__(self, db: Session):
        self.db = db
    
    def get_attempt_result(self, command: GetAttemptResultCommand) -> ResultResponse:
        attempt = self.db.query(Attempt).filter(Attempt.id == command.attempt_id).first()
        if not attempt:
            raise ValueError("Attempt not found")
        
        if attempt.status != "completed":
            raise ValueError("Attempt not completed yet")
        
        test = self.db.query(Test).filter(Test.id == attempt.test_id).first()
        answers = self.db.query(Answer).filter(Answer.attempt_id == command.attempt_id).all()
        
        answer_results = []
        correct_answers = 0
        
        for answer in answers:
            question = self.db.query(Question).filter(Question.id == answer.question_id).first()
            if answer.is_correct:
                correct_answers += 1
            
            answer_results.append(AnswerResult(
                question_id=question.id,
                question_text=question.question_text,
                user_answer=answer.answer_text,
                correct_answer=question.correct_answer,
                is_correct=answer.is_correct,
                marks_obtained=answer.marks_obtained,
                total_marks=1,
                explanation=question.explanation
            ))
        
        return ResultResponse(
            attempt_id=attempt.id,
            user_id=attempt.user_id,
            test_id=attempt.test_id,
            test_title=test.title,
            start_time=attempt.start_time,
            end_time=attempt.end_time,
            total_questions=len(answers),
            correct_answers=correct_answers,
            score=attempt.score,
            percentage=attempt.percentage,
            passed=attempt.passed,
            answers=answer_results
        )
    
    def get_user_results(self, command: GetUserResultsCommand) -> List[ResultSummary]:
        attempts = self.db.query(Attempt).filter(
            Attempt.user_id == command.user_id,
            Attempt.status == "completed"
        ).all()
        
        results = []
        for attempt in attempts:
            test = self.db.query(Test).filter(Test.id == attempt.test_id).first()
            results.append(ResultSummary(
                attempt_id=attempt.id,
                test_title=test.title,
                score=attempt.score,
                percentage=attempt.percentage,
                passed=attempt.passed,
                completed_at=attempt.end_time
            ))
        
        return results
    
    def get_test_analytics(self, command: GetTestAnalyticsCommand):
        attempts = self.db.query(Attempt).filter(
            Attempt.test_id == command.test_id,
            Attempt.status == "completed"
        ).all()
        
        if not attempts:
            return {"message": "No completed attempts found"}
        
        total_attempts = len(attempts)
        passed_attempts = len([a for a in attempts if a.passed])
        average_score = sum(a.score for a in attempts) / total_attempts
        average_percentage = sum(a.percentage for a in attempts) / total_attempts
        
        return {
            "test_id": command.test_id,
            "total_attempts": total_attempts,
            "passed_attempts": passed_attempts,
            "pass_rate": (passed_attempts / total_attempts) * 100,
            "average_score": average_score,
            "average_percentage": average_percentage,
            "highest_score": max(a.score for a in attempts),
            "lowest_score": min(a.score for a in attempts)
        }