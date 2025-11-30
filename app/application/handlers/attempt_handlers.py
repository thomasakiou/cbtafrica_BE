from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List
from app.infrastructure.database.models import Attempt, Answer, Question, Test, Subject
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
        
        # Calculate time taken in seconds
        if attempt.start_time:
            time_taken = int((attempt.end_time - attempt.start_time).total_seconds())
            attempt.time_taken = time_taken
        
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

    def save_practice_attempt(self, command: SavePracticeAttemptCommand) -> AttemptResponse:
        data = command.data
        
        # Calculate percentage and passed status
        percentage = (data.score / data.total_questions) * 100 if data.total_questions > 0 else 0
        passed = percentage >= 50  # Default passing mark of 50%
        
        # Create Attempt Record
        db_attempt = Attempt(
            user_id=data.user_id,
            test_id=None,  # It's a practice test
            subject_id=data.subject_id,
            exam_type_id=data.exam_type_id,
            is_practice=True,
            start_time=datetime.utcnow() - timedelta(seconds=data.time_spent),
            end_time=datetime.utcnow(),
            status="completed",
            score=data.score,
            percentage=percentage,
            passed=passed,
            time_taken=data.time_spent
        )
        self.db.add(db_attempt)
        self.db.commit()
        self.db.refresh(db_attempt)
        
        # Save Answers
        for ans in data.answers:
            db_ans = Answer(
                attempt_id=db_attempt.id,
                question_id=ans.question_id,
                answer_text=ans.answer_text,
                is_correct=ans.is_correct,
                marks_obtained=1 if ans.is_correct else 0,
                time_spent=0 # Not tracked individually for practice currently
            )
            self.db.add(db_ans)
        
        self.db.commit()
        
        # Construct response manually since model_validate might expect test relationship
        return AttemptResponse(
            id=db_attempt.id,
            user_id=db_attempt.user_id,
            test_id=0, # Placeholder
            start_time=db_attempt.start_time,
            end_time=db_attempt.end_time,
            status=db_attempt.status,
            score=db_attempt.score,
            percentage=db_attempt.percentage,
            passed=db_attempt.passed,
            time_taken=db_attempt.time_taken,
            test=None # No test object for practice
        )

    def get_student_attempts(self, user_id: int) -> List[AttemptResponse]:
        attempts = self.db.query(Attempt)\
            .outerjoin(Test, Attempt.test_id == Test.id)\
            .outerjoin(Subject, Attempt.subject_id == Subject.id)\
            .filter(Attempt.user_id == user_id)\
            .filter(Attempt.status == 'completed')\
            .order_by(Attempt.end_time.desc())\
            .all()
        
        result = []
        for attempt in attempts:
            time_taken = attempt.time_taken
            if not time_taken and attempt.start_time and attempt.end_time:
                time_taken = int((attempt.end_time - attempt.start_time).total_seconds())
            
            # Construct the nested test object
            test_data = None
            if attempt.test:
                test_data = {
                    "id": attempt.test.id,
                    "title": attempt.test.title,
                    "subject": attempt.test.subject.name if attempt.test.subject else "Unknown",
                    "total_marks": attempt.test.total_marks,
                    "passing_marks": attempt.test.passing_marks
                }
            elif attempt.is_practice:
                # For practice tests, construct a pseudo-test object or handle in frontend
                # Here we'll provide minimal info so frontend doesn't break
                subject_name = attempt.subject.name if attempt.subject else "Practice"
                test_data = {
                    "id": 0,
                    "title": f"{subject_name} Practice",
                    "subject": subject_name,
                    "total_marks": int(attempt.score / (attempt.percentage/100)) if attempt.percentage and attempt.percentage > 0 else 0,
                    "passing_marks": 50 # Default
                }
            
            attempt_dict = {
                "id": attempt.id,
                "user_id": attempt.user_id,
                "test_id": attempt.test_id if attempt.test_id else 0,
                "start_time": attempt.start_time,
                "end_time": attempt.end_time,
                "status": attempt.status,
                "score": attempt.score,
                "percentage": attempt.percentage,
                "passed": attempt.passed,
                "time_taken": time_taken,
                "test": test_data
            }
            result.append(AttemptResponse(**attempt_dict))
            
        return result

    def get_leaderboard(self) -> List[dict]:
        from app.infrastructure.database.models import User
        from sqlalchemy import func
        
        # Calculate average percentage for each user across all completed attempts
        # Group by user and calculate average, then order by average percentage descending
        user_averages = self.db.query(
            Attempt.user_id,
            func.avg(Attempt.percentage).label('avg_percentage'),
            func.max(Attempt.end_time).label('latest_attempt')
        )\
            .filter(Attempt.status == 'completed')\
            .group_by(Attempt.user_id)\
            .order_by(func.avg(Attempt.percentage).desc())\
            .limit(10)\
            .all()
        
        leaderboard = []
        
        for user_avg in user_averages:
            # Get user details
            user = self.db.query(User).filter(User.id == user_avg.user_id).first()
            
            if not user:
                continue
            
            # Get the most recent attempt for this user to show test/subject info
            latest_attempt = self.db.query(Attempt)\
                .outerjoin(Test, Attempt.test_id == Test.id)\
                .outerjoin(Subject, Attempt.subject_id == Subject.id)\
                .filter(
                    Attempt.user_id == user_avg.user_id,
                    Attempt.status == 'completed'
                )\
                .order_by(Attempt.end_time.desc())\
                .first()
            
            test_title = None
            subject_name = None
            is_practice = False
            
            if latest_attempt:
                test_title = latest_attempt.test.title if latest_attempt.test else None
                subject_name = latest_attempt.subject.name if latest_attempt.subject else None
                is_practice = latest_attempt.is_practice
                
                # If practice test, construct a title
                if is_practice and not test_title:
                    test_title = f"{subject_name} Practice" if subject_name else "Practice Test"
            
            entry = {
                "user_id": user_avg.user_id,
                "full_name": user.full_name,
                "username": user.username,
                "score": round(user_avg.avg_percentage, 2),  # Average percentage rounded to 2 decimals
                "test_title": test_title,
                "subject_name": subject_name,
                "date": user_avg.latest_attempt,
                "is_practice": is_practice
            }
            leaderboard.append(entry)
        
        return leaderboard