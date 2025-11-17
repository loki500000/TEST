"""
Client Vetting Service - CORE FEATURE
Generates comprehensive vetting reports combining trust scores, AI analysis, and historical data
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from freelance_app.services.trust_score_service import trust_score_service
from freelance_app.services.ai_service import ai_service
from freelance_app.models.client import Client
from freelance_app.models.job import Job
from freelance_app.models.scam import ScamReport
from freelance_app.models.company import Company


class VettingService:
    """
    Core service for generating comprehensive client vetting reports

    Combines multiple data sources:
    - Trust Score calculations
    - AI-powered analysis (sentiment, red flags, themes)
    - Historical job data
    - Scam reports
    - Company information
    """

    def __init__(self):
        """Initialize vetting service with required dependencies"""
        self.trust_score_service = trust_score_service
        self.ai_service = ai_service

    def generate_report(
        self,
        client_id: int,
        db: Session,
        include_ai_analysis: bool = True,
        include_company_research: bool = False
    ) -> Dict[str, Any]:
        """
        Generate comprehensive vetting report for a client

        Args:
            client_id: ID of client to vet
            db: Database session
            include_ai_analysis: Whether to include AI-powered analysis
            include_company_research: Whether to research associated company

        Returns:
            Dictionary containing complete vetting report
        """
        # Fetch client data
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client with ID {client_id} not found")

        # Build report sections
        report = {
            "report_id": f"VET-{client_id}-{int(datetime.utcnow().timestamp())}",
            "generated_at": datetime.utcnow().isoformat(),
            "client_info": self._get_client_info(client),
            "trust_score": self._calculate_trust_score(client),
            "historical_data": self._get_historical_data(client, db),
            "scam_reports": self._get_scam_reports(client_id, db),
            "risk_indicators": self._identify_risk_indicators(client, db),
        }

        # Add AI analysis if requested
        if include_ai_analysis:
            report["ai_analysis"] = self._perform_ai_analysis(client, report, db)

        # Add company research if requested and available
        if include_company_research and client.company_id:
            report["company_research"] = self._research_company(client, db)

        # Generate final assessment and recommendations
        report["assessment"] = self._generate_assessment(report)
        report["recommendations"] = self._generate_recommendations(report)

        return report

    def _get_client_info(self, client: Client) -> Dict[str, Any]:
        """Extract basic client information"""
        return {
            "id": client.id,
            "name": client.name,
            "email": client.email,
            "platform": client.platform.name if client.platform else "Unknown",
            "platform_url": client.platform_url,
            "account_created": client.account_created.isoformat() if client.account_created else None,
            "location": client.location,
            "timezone": client.timezone,
            "payment_verified": client.payment_verified,
            "email_verified": client.email_verified,
            "phone_verified": client.phone_verified,
        }

    def _calculate_trust_score(self, client: Client) -> Dict[str, Any]:
        """Calculate comprehensive trust score"""
        # Calculate account age
        account_age_days = 0
        if client.account_created:
            account_age_days = (datetime.utcnow() - client.account_created).days

        # Prepare client data for scoring
        client_data = {
            "account_age_days": account_age_days,
            "payment_verified": client.payment_verified,
            "total_spent": float(client.total_spent) if client.total_spent else 0,
            "total_jobs_posted": client.total_jobs_posted or 0,
            "total_jobs_hired": client.total_jobs_hired or 0,
            "average_rating": float(client.average_rating) if client.average_rating else 0,
            "avg_response_time_hours": float(client.avg_response_time_hours) if client.avg_response_time_hours else 999,
            "total_jobs_started": client.total_jobs_hired or 0,  # Assuming hired jobs are started
            "total_jobs_completed": client.total_jobs_posted or 0,  # Placeholder
        }

        return self.trust_score_service.calculate_score(client_data)

    def _get_historical_data(self, client: Client, db: Session) -> Dict[str, Any]:
        """Retrieve and analyze historical job data"""
        jobs = db.query(Job).filter(Job.client_id == client.id).order_by(Job.created_at.desc()).all()

        job_summaries = []
        for job in jobs[:20]:  # Limit to most recent 20 jobs
            job_summaries.append({
                "id": job.id,
                "title": job.title,
                "budget": float(job.budget) if job.budget else None,
                "status": job.status,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "category": job.category,
            })

        # Calculate statistics
        total_jobs = len(jobs)
        total_budget = sum(float(job.budget) for job in jobs if job.budget)
        avg_budget = total_budget / total_jobs if total_jobs > 0 else 0

        return {
            "total_jobs": total_jobs,
            "total_budget": total_budget,
            "average_budget": avg_budget,
            "recent_jobs": job_summaries,
            "job_categories": self._analyze_job_categories(jobs),
        }

    def _get_scam_reports(self, client_id: int, db: Session) -> List[Dict[str, Any]]:
        """Retrieve scam reports related to this client"""
        reports = db.query(ScamReport).filter(ScamReport.client_id == client_id).all()

        return [
            {
                "id": report.id,
                "report_type": report.report_type,
                "severity": report.severity,
                "description": report.description,
                "status": report.status,
                "reported_at": report.reported_at.isoformat() if report.reported_at else None,
            }
            for report in reports
        ]

    def _identify_risk_indicators(self, client: Client, db: Session) -> List[Dict[str, Any]]:
        """Identify potential risk indicators"""
        indicators = []

        # Check account age
        if client.account_created:
            days_old = (datetime.utcnow() - client.account_created).days
            if days_old < 30:
                indicators.append({
                    "type": "new_account",
                    "severity": "medium",
                    "description": f"Account is only {days_old} days old",
                })

        # Check payment verification
        if not client.payment_verified:
            indicators.append({
                "type": "payment_not_verified",
                "severity": "high",
                "description": "Payment method not verified",
            })

        # Check spending history
        if client.total_spent and client.total_spent < 50:
            indicators.append({
                "type": "low_spending",
                "severity": "medium",
                "description": f"Low total spending: ${client.total_spent}",
            })

        # Check for scam reports
        scam_reports = db.query(ScamReport).filter(ScamReport.client_id == client.id).count()
        if scam_reports > 0:
            indicators.append({
                "type": "scam_reports",
                "severity": "critical",
                "description": f"Client has {scam_reports} scam report(s)",
            })

        # Check rating
        if client.average_rating and client.average_rating < 3.0:
            indicators.append({
                "type": "low_rating",
                "severity": "high",
                "description": f"Low average rating: {client.average_rating}/5.0",
            })

        # Check response time
        if client.avg_response_time_hours and client.avg_response_time_hours > 48:
            indicators.append({
                "type": "slow_response",
                "severity": "low",
                "description": f"Slow response time: {client.avg_response_time_hours} hours average",
            })

        return indicators

    def _perform_ai_analysis(self, client: Client, report: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Perform AI-powered analysis of client"""
        analysis = {}

        # Get recent jobs for context
        jobs = db.query(Job).filter(Job.client_id == client.id).order_by(Job.created_at.desc()).limit(5).all()

        # Prepare client data for AI analysis
        client_data_for_ai = {
            "name": client.name,
            "account_age_days": (datetime.utcnow() - client.account_created).days if client.account_created else 0,
            "total_jobs_posted": client.total_jobs_posted or 0,
            "payment_verified": client.payment_verified,
            "average_rating": float(client.average_rating) if client.average_rating else 0,
            "total_spent": float(client.total_spent) if client.total_spent else 0,
            "avg_response_time_hours": float(client.avg_response_time_hours) if client.avg_response_time_hours else 999,
            "completion_rate": 0,  # Placeholder
            "recent_reviews": [],  # Placeholder
        }

        # Detect red flags
        try:
            analysis["red_flags"] = self.ai_service.detect_red_flags(client_data_for_ai)
        except Exception as e:
            analysis["red_flags"] = {"error": str(e)}

        # Analyze job descriptions if available
        if jobs:
            job_descriptions = [job.description for job in jobs if job.description]
            if job_descriptions:
                try:
                    analysis["job_themes"] = self.ai_service.extract_themes(job_descriptions)
                except Exception as e:
                    analysis["job_themes"] = {"error": str(e)}

        # Generate AI summary
        try:
            analysis["ai_summary"] = self.ai_service.generate_vetting_summary({
                "client_name": client.name,
                "trust_score": report["trust_score"]["total_score"],
                "risk_level": report["trust_score"]["risk_level"],
                "red_flags": analysis.get("red_flags", {}).get("red_flags", []),
                "payment_verified": client.payment_verified,
                "total_jobs": client.total_jobs_posted or 0,
                "average_rating": float(client.average_rating) if client.average_rating else 0,
            })
        except Exception as e:
            analysis["ai_summary"] = f"Unable to generate AI summary: {str(e)}"

        return analysis

    def _research_company(self, client: Client, db: Session) -> Dict[str, Any]:
        """Research associated company using AI"""
        if not client.company_id:
            return {}

        company = db.query(Company).filter(Company.id == client.company_id).first()
        if not company:
            return {}

        try:
            research = self.ai_service.research_company(
                company.name,
                additional_context=company.description
            )
            return research
        except Exception as e:
            return {"error": str(e)}

    def _analyze_job_categories(self, jobs: List[Job]) -> Dict[str, int]:
        """Analyze distribution of job categories"""
        categories = {}
        for job in jobs:
            if job.category:
                categories[job.category] = categories.get(job.category, 0) + 1
        return categories

    def _generate_assessment(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall assessment based on all report data"""
        trust_score = report["trust_score"]["total_score"]
        risk_level = report["trust_score"]["risk_level"]
        scam_reports_count = len(report["scam_reports"])
        risk_indicators_count = len(report["risk_indicators"])

        # Determine overall recommendation
        if risk_level == "critical" or scam_reports_count > 0:
            recommendation = "AVOID"
            confidence = "high"
        elif risk_level == "high" or risk_indicators_count > 3:
            recommendation = "PROCEED_WITH_CAUTION"
            confidence = "high"
        elif risk_level == "medium":
            recommendation = "PROCEED_WITH_CAUTION"
            confidence = "medium"
        else:
            recommendation = "SAFE_TO_PROCEED"
            confidence = "high"

        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "trust_score": trust_score,
            "risk_level": risk_level,
            "scam_reports_count": scam_reports_count,
            "risk_indicators_count": risk_indicators_count,
        }

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        trust_score = report["trust_score"]["total_score"]
        risk_level = report["trust_score"]["risk_level"]

        # Based on trust score
        if trust_score < 40:
            recommendations.append("⚠️ CRITICAL: This client has a very low trust score. Consider avoiding this opportunity.")
        elif trust_score < 60:
            recommendations.append("⚠️ Warning: Low trust score. Request milestone payments and clear contracts.")
        elif trust_score < 80:
            recommendations.append("Moderate trust score. Use standard precautions and clear communication.")
        else:
            recommendations.append("✓ High trust score. Client appears reliable based on historical data.")

        # Based on risk indicators
        for indicator in report["risk_indicators"]:
            if indicator["severity"] == "critical":
                recommendations.append(f"🚨 CRITICAL: {indicator['description']}")
            elif indicator["severity"] == "high":
                recommendations.append(f"⚠️ {indicator['description']}")

        # Based on scam reports
        if report["scam_reports"]:
            recommendations.append(f"🚨 SCAM ALERT: Client has {len(report['scam_reports'])} scam report(s). Strongly recommend avoiding.")

        # Payment verification
        if not report["client_info"]["payment_verified"]:
            recommendations.append("Require payment verification before starting work.")

        # AI-based recommendations
        if "ai_analysis" in report:
            ai_recs = report["ai_analysis"].get("red_flags", {}).get("recommendations", [])
            recommendations.extend(ai_recs)

        # General best practices
        if trust_score < 80:
            recommendations.extend([
                "Request detailed project scope and milestones",
                "Use escrow or milestone-based payments",
                "Keep all communication on the platform",
                "Document all agreements in writing",
            ])

        return recommendations


# Singleton instance
vetting_service = VettingService()
