"""Shortlisting agent to evaluate and shortlist eligible candidates."""
from typing import Dict, Any, List
import random
from agentic_framework.agent_base import Agent
from database.vectorstore import VectorStore

class ShortlistingAgent(Agent):
    """Agent responsible for shortlisting eligible candidates."""
    
    def __init__(self):
        """Initialize the shortlisting agent."""
        system_prompt = """
        You are a Shortlisting Agent for a university admission process.
        Your task is to evaluate applications that have passed document verification
        and determine if they meet the eligibility criteria for admission.
        
        You need to:
        1. Review the candidate's eligibility score
        2. Check if the program they applied for has available capacity
        3. Rank candidates based on their credentials
        4. Make a shortlisting decision
        
        Be fair and objective in your evaluation. Follow the university's eligibility criteria strictly.
        Provide clear reasoning for your decisions.
        """
        
        super().__init__(name="Shortlisting Agent", system_prompt=system_prompt)
        self.vector_store = VectorStore()
        
        # Load knowledge base for reference
        self.vector_store.load_knowledge_base()
    
    def get_eligibility_criteria(self) -> Dict[str, Any]:
        """Get eligibility criteria from the knowledge base."""
        criteria_info = self.vector_store.search("eligibility criteria", n_results=1)
        
        # Default criteria
        criteria = {
            "min_gpa": 3.0,
            "required_documents": [
                "application_form",
                "academic_transcripts",
                "id_passport",
                "recommendation_letters",
                "statement_of_purpose"
            ],
            "additional_requirements": []
        }
        
        # Update with information from knowledge base if available
        if criteria_info:
            criteria_text = criteria_info[0]["text"]
            
            # Extract minimum GPA
            import re
            min_gpa_pattern = r"minimum GPA of ([\d.]+)"
            min_gpa_match = re.search(min_gpa_pattern, criteria_text)
            if min_gpa_match:
                criteria["min_gpa"] = float(min_gpa_match.group(1))
        
        return criteria
    
    def get_program_capacity(self) -> Dict[str, int]:
        """Get program capacity information."""
        capacity_info = self.vector_store.search("university capacity", n_results=1)
        
        # Default capacities
        capacities = {
            "Computer Science": 100,
            "Business Administration": 150,
            "Engineering": 120,
            "Medicine": 80,
            "Arts and Humanities": 200
        }
        
        # Update with information from knowledge base if available
        if capacity_info:
            capacity_text = capacity_info[0]["text"]
            
            # Extract capacities for each program
            import re
            capacity_pattern = r"([\w\s]+):\s*(\d+)"
            capacity_matches = re.findall(capacity_pattern, capacity_text)
            
            for program, capacity in capacity_matches:
                capacities[program.strip()] = int(capacity)
        
        return capacities
    
    def check_program_availability(self, program: str) -> bool:
        """Check if the program has available capacity."""
        capacities = self.get_program_capacity()
        
        # Simulate current enrollment
        current_enrollment = {
            program: random.randint(0, capacity) 
            for program, capacity in capacities.items()
        }
        
        # Check if program exists and has capacity
        if program not in capacities:
            return False
        
        return current_enrollment.get(program, 0) < capacities.get(program, 0)
    
    def rank_application(self, application: Dict[str, Any]) -> float:
        """Rank the application based on criteria."""
        # Use eligibility score (GPA) as the base
        base_score = application.eligibility_score or 0
        
        # Add bonus for complete documentation
        if application.verification_notes and "success" in application.verification_notes:
            base_score += 0.5
        
        # Randomize a bit to simulate other factors
        random_factor = random.uniform(-0.2, 0.2)
        
        return base_score + random_factor
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the application for shortlisting."""
        application = state["application"]
        
        # Only process applications that have verified documents
        if application.status != "documents_verified":
            return state
        
        # Get eligibility criteria
        criteria = self.get_eligibility_criteria()
        
        # Check eligibility score against minimum requirements
        if application.eligibility_score < criteria["min_gpa"]:
            shortlisting_notes = f"Application rejected: Eligibility score ({application.eligibility_score}) below minimum requirement ({criteria['min_gpa']})"
            
            # Update application status
            application.status = "rejected"
            application.shortlisting_notes = shortlisting_notes
            
            # Log the rejection
            state["history"].append({
                "agent": self.name,
                "action": "application_rejection",
                "reason": shortlisting_notes
            })
            
            return state
        
        # Check program availability
        # For demonstration, assume the program is from context or default to Computer Science
        program = state["context"].get("program", "Computer Science")
        
        if not self.check_program_availability(program):
            shortlisting_notes = f"Application rejected: No capacity available in the {program} program"
            
            # Update application status
            application.status = "rejected"
            application.shortlisting_notes = shortlisting_notes
            
            # Log the rejection
            state["history"].append({
                "agent": self.name,
                "action": "application_rejection",
                "reason": shortlisting_notes
            })
            
            return state
        
        # Rank the application
        rank_score = self.rank_application(application)
        
        # Shortlist the application
        shortlisting_notes = f"Application shortlisted with rank score: {rank_score:.2f}"
        
        # Update application status
        application.status = "shortlisted"
        application.shortlisting_notes = shortlisting_notes
        
        # Log the shortlisting
        state["history"].append({
            "agent": self.name,
            "action": "application_shortlisting",
            "rank_score": rank_score,
            "notes": shortlisting_notes
        })
        
        # Update current agent
        state["current_agent"] = "student_counselor"
        
        return state