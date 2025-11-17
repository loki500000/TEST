"""
AI Service for Freelance Vetting Application
Leverages Groq API for AI-powered analysis and insights
"""

import sys
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add parent directory to path to import groq modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.groq_ttt import chat_completion
from src.groq_compound import compound_chat
from freelance_app.config import settings


class AIService:
    """
    AI-powered service for analyzing clients, jobs, and companies
    Uses Groq API for advanced language processing
    """

    def __init__(self):
        """Initialize AI service with Groq API configuration"""
        self.model = settings.GROQ_MODEL
        self.temperature = settings.GROQ_TEMPERATURE
        self.api_key = settings.GROQ_API_KEY

        if not self.api_key:
            raise ValueError("GROQ_API_KEY must be set in environment variables")

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text (reviews, job descriptions, etc.)

        Args:
            text: Text to analyze

        Returns:
            Dict containing sentiment analysis results
        """
        messages = [
            {
                "role": "system",
                "content": "You are an expert at sentiment analysis. Analyze the text and return a JSON response with: sentiment (positive/negative/neutral), score (0-100), and key_points (list of notable observations)."
            },
            {
                "role": "user",
                "content": f"Analyze the sentiment of this text:\n\n{text}"
            }
        ]

        try:
            response = chat_completion(
                messages=messages,
                model=self.model,
                temperature=0.3,
                response_format={"type": "json_object"},
                save_to_file=False
            )

            # Parse the response
            import json
            result = json.loads(response.text)
            return result

        except Exception as e:
            return {
                "sentiment": "neutral",
                "score": 50,
                "key_points": [],
                "error": str(e)
            }

    def extract_themes(self, texts: List[str]) -> Dict[str, Any]:
        """
        Extract common themes from multiple texts (reviews, communications)

        Args:
            texts: List of texts to analyze

        Returns:
            Dict containing extracted themes and patterns
        """
        combined_text = "\n---\n".join(texts[:10])  # Limit to 10 texts to avoid token limits

        messages = [
            {
                "role": "system",
                "content": "You are an expert at thematic analysis. Extract and summarize key themes, patterns, and concerns from the texts. Return a JSON response with: themes (list of themes with descriptions), positive_patterns (list), negative_patterns (list), and overall_summary (string)."
            },
            {
                "role": "user",
                "content": f"Extract themes from these texts:\n\n{combined_text}"
            }
        ]

        try:
            response = chat_completion(
                messages=messages,
                model=self.model,
                temperature=0.4,
                response_format={"type": "json_object"},
                save_to_file=False
            )

            import json
            result = json.loads(response.text)
            return result

        except Exception as e:
            return {
                "themes": [],
                "positive_patterns": [],
                "negative_patterns": [],
                "overall_summary": "",
                "error": str(e)
            }

    def detect_red_flags(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect red flags in client profile and behavior

        Args:
            client_data: Dictionary containing client information

        Returns:
            Dict containing detected red flags and risk assessment
        """
        # Format client data for analysis
        data_summary = f"""
Client Profile:
- Name: {client_data.get('name', 'Unknown')}
- Account Age: {client_data.get('account_age_days', 0)} days
- Total Jobs Posted: {client_data.get('total_jobs_posted', 0)}
- Payment Verified: {client_data.get('payment_verified', False)}
- Average Rating: {client_data.get('average_rating', 0)}
- Total Spent: ${client_data.get('total_spent', 0)}
- Response Time: {client_data.get('avg_response_time_hours', 0)} hours
- Completion Rate: {client_data.get('completion_rate', 0)}%
- Recent Reviews: {client_data.get('recent_reviews', [])}
"""

        messages = [
            {
                "role": "system",
                "content": "You are an expert at fraud detection and risk assessment for freelance platforms. Analyze the client profile and identify potential red flags or concerning patterns. Return a JSON response with: red_flags (list of flag objects with 'flag', 'severity' (low/medium/high), and 'description'), risk_level (low/medium/high/critical), risk_score (0-100), and recommendations (list of strings)."
            },
            {
                "role": "user",
                "content": f"Analyze this client profile for red flags:\n\n{data_summary}"
            }
        ]

        try:
            response = chat_completion(
                messages=messages,
                model=self.model,
                temperature=0.2,
                response_format={"type": "json_object"},
                save_to_file=False
            )

            import json
            result = json.loads(response.text)
            return result

        except Exception as e:
            return {
                "red_flags": [],
                "risk_level": "unknown",
                "risk_score": 50,
                "recommendations": [],
                "error": str(e)
            }

    def research_company(self, company_name: str, additional_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Research company using AI-powered web search and analysis
        Uses compound model for tool-augmented research

        Args:
            company_name: Name of the company to research
            additional_context: Optional additional context about the company

        Returns:
            Dict containing company research results
        """
        context_str = f"\nAdditional context: {additional_context}" if additional_context else ""

        messages = [
            {
                "role": "system",
                "content": "You are a business research expert. Research the company and provide insights about its legitimacy, reputation, and business practices. Focus on finding information about the company's history, reviews, complaints, and general reputation."
            },
            {
                "role": "user",
                "content": f"Research this company: {company_name}{context_str}\n\nProvide a comprehensive summary including: company overview, reputation assessment, notable reviews or complaints, and legitimacy indicators."
            }
        ]

        try:
            # Use compound model for enhanced research capabilities
            response = compound_chat(
                messages=messages,
                model="compound-beta",
                save_to_file=False
            )

            return {
                "company_name": company_name,
                "research_summary": response.text,
                "timestamp": str(Path(__file__).stat().st_mtime)
            }

        except Exception as e:
            return {
                "company_name": company_name,
                "research_summary": f"Unable to research company at this time.",
                "error": str(e),
                "timestamp": str(Path(__file__).stat().st_mtime)
            }

    def parse_nl_query(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language search query into structured filters

        Args:
            query: Natural language query from user

        Returns:
            Dict containing parsed query parameters
        """
        messages = [
            {
                "role": "system",
                "content": """You are a query parser for a freelance job search platform. Parse natural language queries into structured filters.

Return a JSON response with these fields:
- keywords: List of search keywords
- min_budget: Minimum budget (number or null)
- max_budget: Maximum budget (number or null)
- min_trust_score: Minimum trust score 0-100 (number or null)
- payment_verified: Boolean or null
- location: Location string or null
- job_type: Job type or null
- sort_by: Field to sort by (relevance, budget, trust_score, date)
- filters: Dictionary of additional filters

Examples:
"Find web development jobs over $500 from verified clients" -> {keywords: ["web development"], min_budget: 500, payment_verified: true}
"High trust score clients in USA" -> {min_trust_score: 80, location: "USA"}
"""
            },
            {
                "role": "user",
                "content": f"Parse this query: {query}"
            }
        ]

        try:
            response = chat_completion(
                messages=messages,
                model=self.model,
                temperature=0.2,
                response_format={"type": "json_object"},
                save_to_file=False
            )

            import json
            result = json.loads(response.text)
            return result

        except Exception as e:
            return {
                "keywords": [query],
                "min_budget": None,
                "max_budget": None,
                "min_trust_score": None,
                "payment_verified": None,
                "location": None,
                "job_type": None,
                "sort_by": "relevance",
                "filters": {},
                "error": str(e)
            }

    def generate_vetting_summary(self, vetting_data: Dict[str, Any]) -> str:
        """
        Generate a comprehensive AI-powered summary of vetting report

        Args:
            vetting_data: Complete vetting report data

        Returns:
            String containing executive summary
        """
        # Format vetting data
        summary_input = f"""
Client: {vetting_data.get('client_name', 'Unknown')}
Trust Score: {vetting_data.get('trust_score', 0)}/100
Risk Level: {vetting_data.get('risk_level', 'Unknown')}
Red Flags: {len(vetting_data.get('red_flags', []))}
Payment Verified: {vetting_data.get('payment_verified', False)}
Total Jobs: {vetting_data.get('total_jobs', 0)}
Average Rating: {vetting_data.get('average_rating', 0)}
"""

        messages = [
            {
                "role": "system",
                "content": "You are an expert at creating executive summaries for client vetting reports. Create a concise, professional summary (2-3 paragraphs) that highlights key findings and provides clear recommendations."
            },
            {
                "role": "user",
                "content": f"Create an executive summary for this vetting report:\n\n{summary_input}"
            }
        ]

        try:
            response = chat_completion(
                messages=messages,
                model=self.model,
                temperature=0.5,
                save_to_file=False
            )

            return response.text.strip()

        except Exception as e:
            return f"Unable to generate summary. Trust Score: {vetting_data.get('trust_score', 0)}/100. Risk Level: {vetting_data.get('risk_level', 'Unknown')}."


# Singleton instance
ai_service = AIService()
