"""
Trust Score Service - Calculate client trustworthiness scores
Implements a weighted scoring algorithm based on 7 key factors
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from freelance_app.config import settings


class TrustScoreService:
    """
    Service for calculating trust scores (0-100) based on multiple factors

    Scoring Factors:
    1. Account Age (20%) - Older accounts are more trustworthy
    2. Payment Verified (15%) - Payment method verification
    3. Total Spent (15%) - Track record of spending on platform
    4. Hire Rate (15%) - Percentage of posted jobs that result in hires
    5. Average Rating (20%) - Average rating from freelancers
    6. Response Time (10%) - How quickly client responds
    7. Completion Rate (5%) - Percentage of jobs completed successfully
    """

    def __init__(self):
        """Initialize with scoring weights from configuration"""
        self.weights = settings.TRUST_SCORE_WEIGHTS

    def calculate_score(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive trust score for a client

        Args:
            client_data: Dictionary containing client metrics
                - account_age_days: Age of account in days
                - payment_verified: Boolean indicating payment verification
                - total_spent: Total amount spent on platform
                - total_jobs_posted: Total jobs posted
                - total_jobs_hired: Total jobs that resulted in hire
                - average_rating: Average rating (0-5)
                - avg_response_time_hours: Average response time in hours
                - total_jobs_completed: Total jobs completed
                - total_jobs_started: Total jobs started

        Returns:
            Dictionary containing:
                - total_score: Overall trust score (0-100)
                - breakdown: Score breakdown by factor
                - grade: Letter grade (A+ to F)
                - risk_level: Risk assessment (low/medium/high/critical)
        """
        breakdown = {}

        # 1. Account Age Score (20%)
        account_age_days = client_data.get('account_age_days', 0)
        breakdown['account_age'] = self._calculate_account_age_score(account_age_days)

        # 2. Payment Verified Score (15%)
        payment_verified = client_data.get('payment_verified', False)
        breakdown['payment_verified'] = self._calculate_payment_verified_score(payment_verified)

        # 3. Total Spent Score (15%)
        total_spent = client_data.get('total_spent', 0)
        breakdown['total_spent'] = self._calculate_spending_score(total_spent)

        # 4. Hire Rate Score (15%)
        total_jobs_posted = client_data.get('total_jobs_posted', 0)
        total_jobs_hired = client_data.get('total_jobs_hired', 0)
        breakdown['hire_rate'] = self._calculate_hire_rate_score(
            total_jobs_posted, total_jobs_hired
        )

        # 5. Average Rating Score (20%)
        average_rating = client_data.get('average_rating', 0)
        breakdown['average_rating'] = self._calculate_rating_score(average_rating)

        # 6. Response Time Score (10%)
        avg_response_time_hours = client_data.get('avg_response_time_hours', 999)
        breakdown['response_time'] = self._calculate_response_time_score(
            avg_response_time_hours
        )

        # 7. Completion Rate Score (5%)
        total_jobs_started = client_data.get('total_jobs_started', 0)
        total_jobs_completed = client_data.get('total_jobs_completed', 0)
        breakdown['completion_rate'] = self._calculate_completion_rate_score(
            total_jobs_started, total_jobs_completed
        )

        # Calculate weighted total score
        total_score = sum(
            breakdown[factor] * self.weights[factor]
            for factor in self.weights.keys()
        )

        # Ensure score is within 0-100 range
        total_score = max(0, min(100, total_score))

        return {
            'total_score': round(total_score, 2),
            'breakdown': {k: round(v, 2) for k, v in breakdown.items()},
            'grade': self._calculate_grade(total_score),
            'risk_level': self._calculate_risk_level(total_score)
        }

    def _calculate_account_age_score(self, age_days: int) -> float:
        """
        Calculate score based on account age

        Scoring:
        - 0-30 days: 20-40
        - 31-90 days: 40-60
        - 91-180 days: 60-75
        - 181-365 days: 75-90
        - 365+ days: 90-100
        """
        if age_days < 0:
            return 0.0
        elif age_days <= 30:
            return 20 + (age_days / 30) * 20  # 20-40
        elif age_days <= 90:
            return 40 + ((age_days - 30) / 60) * 20  # 40-60
        elif age_days <= 180:
            return 60 + ((age_days - 90) / 90) * 15  # 60-75
        elif age_days <= 365:
            return 75 + ((age_days - 180) / 185) * 15  # 75-90
        else:
            # Cap at 100, with diminishing returns
            return min(100, 90 + min(10, (age_days - 365) / 365 * 10))

    def _calculate_payment_verified_score(self, verified: bool) -> float:
        """
        Calculate score based on payment verification

        Scoring:
        - Verified: 100
        - Not verified: 20
        """
        return 100.0 if verified else 20.0

    def _calculate_spending_score(self, total_spent: float) -> float:
        """
        Calculate score based on total spending

        Scoring:
        - $0: 0
        - $1-100: 20-40
        - $101-500: 40-60
        - $501-2000: 60-80
        - $2001-10000: 80-95
        - $10000+: 95-100
        """
        if total_spent <= 0:
            return 0.0
        elif total_spent <= 100:
            return 20 + (total_spent / 100) * 20
        elif total_spent <= 500:
            return 40 + ((total_spent - 100) / 400) * 20
        elif total_spent <= 2000:
            return 60 + ((total_spent - 500) / 1500) * 20
        elif total_spent <= 10000:
            return 80 + ((total_spent - 2000) / 8000) * 15
        else:
            return min(100, 95 + ((total_spent - 10000) / 10000) * 5)

    def _calculate_hire_rate_score(self, jobs_posted: int, jobs_hired: int) -> float:
        """
        Calculate score based on hire rate (jobs hired / jobs posted)

        Scoring:
        - No jobs posted: 50 (neutral)
        - 0-20% hire rate: 10-30
        - 21-40%: 30-50
        - 41-60%: 50-70
        - 61-80%: 70-85
        - 81-100%: 85-100
        """
        if jobs_posted == 0:
            return 50.0  # Neutral score for new accounts

        hire_rate = (jobs_hired / jobs_posted) * 100

        if hire_rate <= 20:
            return 10 + (hire_rate / 20) * 20
        elif hire_rate <= 40:
            return 30 + ((hire_rate - 20) / 20) * 20
        elif hire_rate <= 60:
            return 50 + ((hire_rate - 40) / 20) * 20
        elif hire_rate <= 80:
            return 70 + ((hire_rate - 60) / 20) * 15
        else:
            return 85 + ((hire_rate - 80) / 20) * 15

    def _calculate_rating_score(self, average_rating: float) -> float:
        """
        Calculate score based on average rating (0-5 scale)

        Scoring:
        - 0-1: 0-20
        - 1-2: 20-40
        - 2-3: 40-60
        - 3-4: 60-80
        - 4-5: 80-100
        """
        if average_rating < 0:
            return 0.0
        elif average_rating > 5:
            return 100.0

        return (average_rating / 5) * 100

    def _calculate_response_time_score(self, avg_hours: float) -> float:
        """
        Calculate score based on average response time

        Scoring:
        - 0-1 hours: 100
        - 1-6 hours: 90-100
        - 6-24 hours: 70-90
        - 24-48 hours: 50-70
        - 48-72 hours: 30-50
        - 72+ hours: 0-30
        """
        if avg_hours <= 1:
            return 100.0
        elif avg_hours <= 6:
            return 90 + (1 - (avg_hours - 1) / 5) * 10
        elif avg_hours <= 24:
            return 70 + (1 - (avg_hours - 6) / 18) * 20
        elif avg_hours <= 48:
            return 50 + (1 - (avg_hours - 24) / 24) * 20
        elif avg_hours <= 72:
            return 30 + (1 - (avg_hours - 48) / 24) * 20
        else:
            return max(0, 30 - ((avg_hours - 72) / 72) * 30)

    def _calculate_completion_rate_score(self, jobs_started: int, jobs_completed: int) -> float:
        """
        Calculate score based on job completion rate

        Scoring:
        - No jobs started: 50 (neutral)
        - 0-50% completion: 0-50
        - 51-80%: 50-80
        - 81-100%: 80-100
        """
        if jobs_started == 0:
            return 50.0  # Neutral for new accounts

        completion_rate = (jobs_completed / jobs_started) * 100

        if completion_rate <= 50:
            return completion_rate
        elif completion_rate <= 80:
            return 50 + ((completion_rate - 50) / 30) * 30
        else:
            return 80 + ((completion_rate - 80) / 20) * 20

    def _calculate_grade(self, score: float) -> str:
        """
        Convert numerical score to letter grade

        Grading Scale:
        - 97-100: A+
        - 93-96: A
        - 90-92: A-
        - 87-89: B+
        - 83-86: B
        - 80-82: B-
        - 77-79: C+
        - 73-76: C
        - 70-72: C-
        - 67-69: D+
        - 63-66: D
        - 60-62: D-
        - 0-59: F
        """
        if score >= 97:
            return "A+"
        elif score >= 93:
            return "A"
        elif score >= 90:
            return "A-"
        elif score >= 87:
            return "B+"
        elif score >= 83:
            return "B"
        elif score >= 80:
            return "B-"
        elif score >= 77:
            return "C+"
        elif score >= 73:
            return "C"
        elif score >= 70:
            return "C-"
        elif score >= 67:
            return "D+"
        elif score >= 63:
            return "D"
        elif score >= 60:
            return "D-"
        else:
            return "F"

    def _calculate_risk_level(self, score: float) -> str:
        """
        Determine risk level based on trust score

        Risk Levels:
        - 80-100: low
        - 60-79: medium
        - 40-59: high
        - 0-39: critical
        """
        if score >= 80:
            return "low"
        elif score >= 60:
            return "medium"
        elif score >= 40:
            return "high"
        else:
            return "critical"


# Singleton instance
trust_score_service = TrustScoreService()
