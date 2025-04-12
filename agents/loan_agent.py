"""Loan processing agent to handle student loan applications."""
from typing import Dict, Any, List
import random
from agentic_framework.agent_base import Agent
from database.vectorstore import VectorStore

class LoanAgent(Agent):
    """Agent responsible for processing student loan applications."""
    
    def __init__(self):
        """Initialize the loan agent."""
        system_prompt = """
        You are a Loan Processing Agent for a university's financial aid office.
        Your task is to evaluate loan applications from admitted students.
        
        You need to:
        1. Review the student's loan application
        2. Evaluate their eligibility based on financial need
        3. Determine the loan amount they qualify for
        4. Process the loan approval or rejection
        
        Be fair and thorough in your evaluation. Follow the university's loan policies strictly.
        Clearly explain the reason for approval or rejection.
        """
        
        super().__init__(name="Loan Agent", system_prompt=system_prompt)
        self.vector_store = VectorStore()
        
        # Load knowledge base for reference
        self.vector_store.load_knowledge_base()
    
    def get_loan_policies(self) -> Dict[str, Any]:
        """Get loan policies from the knowledge base."""
        policy_info = self.vector_store.search("loan policy", n_results=1)
        
        # Default policies
        policies = {
            "max_loan_amount": 20000,
            "interest_rate": 4.0,
            "repayment_period_years": 10,
            "grace_period_months": 6,
            "minimum_income_requirement": 25000,
            "credit_score_requirement": 650
        }
        
        # Update with information from knowledge base if available
        if policy_info:
            policy_text = policy_info[0]["text"]
            
            # Extract policy details
            import re
            max_loan_pattern = r"maximum loan amount of \$([\d,]+)"
            max_loan_match = re.search(max_loan_pattern, policy_text)
            if max_loan_match:
                policies["max_loan_amount"] = int(max_loan_match.group(1).replace(",", ""))
            
            interest_pattern = r"interest rate of ([\d.]+)%"
            interest_match = re.search(interest_pattern, policy_text)
            if interest_match:
                policies["interest_rate"] = float(interest_match.group(1))
        
        return policies
    
    def calculate_eligibility(self, application: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate loan eligibility based on student information."""
        # Get loan policies
        policies = self.get_loan_policies()
        
        # In a real system, this would use actual student financial data
        # For this demo, we'll simulate financial assessment
        
        # Simulate family income (would come from application in real system)
        family_income = random.randint(20000, 100000)
        
        # Simulate credit score (would come from application in real system)
        credit_score = random.randint(500, 800)
        
        # Calculate eligibility
        eligible = (
            family_income >= policies["minimum_income_requirement"] and
            credit_score >= policies["credit_score_requirement"]
        )
        
        # Calculate loan amount based on eligibility
        max_amount = policies["max_loan_amount"]
        
        if eligible:
            if family_income < 40000:
                loan_amount = max_amount
            elif family_income < 60000:
                loan_amount = max_amount * 0.75
            elif family_income < 80000:
                loan_amount = max_amount * 0.5
            else:
                loan_amount = max_amount * 0.25
        else:
            loan_amount = 0
        
        return {
            "eligible": eligible,
            "loan_amount": int(loan_amount),
            "family_income": family_income,
            "credit_score": credit_score,
            "interest_rate": policies["interest_rate"],
            "repayment_period_years": policies["repayment_period_years"],
            "reasons": [] if eligible else [
                "Insufficient family income" if family_income < policies["minimum_income_requirement"] else None,
                "Insufficient credit score" if credit_score < policies["credit_score_requirement"] else None
            ]
        }
    
    def generate_loan_approval_letter(self, student_name: str, loan_details: Dict[str, Any]) -> str:
        """Generate a loan approval letter."""
        # Get template from knowledge base
        template_info = self.vector_store.search("loan_approval", n_results=1)
        
        if template_info and template_info[0]["text"]:
            template = template_info[0]["text"]
            # Replace placeholders with actual data
            letter = template.replace("[STUDENT_NAME]", student_name)
            letter = letter.replace("[LOAN_AMOUNT]", f"${loan_details['loan_amount']:,}")
            letter = letter.replace("[INTEREST_RATE]", f"{loan_details['interest_rate']}%")
            letter = letter.replace("[REPAYMENT_PERIOD]", f"{loan_details['repayment_period_years']} years")
            return letter
        
        # Default letter if template not found
        return f"""
        Dear {student_name},
        
        We are pleased to inform you that your loan application has been approved.
        
        Loan Details:
        - Amount: ${loan_details['loan_amount']:,}
        - Interest Rate: {loan_details['interest_rate']}%
        - Repayment Period: {loan_details['repayment_period_years']} years
        - Grace Period: 6 months after graduation
        
        Please review and sign the attached loan agreement within 5 business days.
        
        If you have any questions, please contact the financial aid office.
        
        Best regards,
        University Financial Aid Office
        """
    
    def generate_loan_rejection_letter(self, student_name: str, reasons: List[str]) -> str:
        """Generate a loan rejection letter."""
        reasons_list = "\n".join([f"- {reason}" for reason in reasons if reason])
        
        return f"""
        Dear {student_name},
        
        We regret to inform you that your loan application has been rejected.
        
        Reasons for rejection:
        {reasons_list}
        
        If you would like to discuss alternative financing options or have questions about the decision,
        please contact our financial aid office.
        
        Best regards,
        University Financial Aid Office
        """
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the loan application."""
        application = state["application"]
        
        # Only process loan requested applications
        if application.status != "loan_requested":
            return state
        
        # Calculate loan eligibility
        loan_details = self.calculate_eligibility(application)
        
        # Store loan details in application state
        application.loan_details = loan_details
        
        if loan_details["eligible"]:
            # Generate loan approval letter
            approval_letter = self.generate_loan_approval_letter(application.student_name, loan_details)
            
            # Add to communications
            application.communications.append({
                "type": "letter",
                "subject": "Loan Application Approved",
                "content": approval_letter,
                "timestamp": "2023-05-20T10:15:00Z"  # In a real app, use actual timestamp
            })
            
            # Update application status
            application.status = "loan_approved"
            
            # Log the approval
            state["history"].append({
                "agent": self.name,
                "action": "loan_approval",
                "loan_amount": loan_details["loan_amount"],
                "notes": "Loan application approved"
            })
        else:
            # Generate loan rejection letter
            rejection_letter = self.generate_loan_rejection_letter(application.student_name, loan_details["reasons"])
            
            # Add to communications
            application.communications.append({
                "type": "letter",
                "subject": "Loan Application Rejected",
                "content": rejection_letter,
                "timestamp": "2023-05-20T10:15:00Z"  # In a real app, use actual timestamp
            })
            
            # Update application status
            application.status = "loan_rejected"
            
            # Log the rejection
            state["history"].append({
                "agent": self.name,
                "action": "loan_rejection",
                "reasons": loan_details["reasons"],
                "notes": "Loan application rejected"
            })
        
        # Update current agent
        state["current_agent"] = "admission_officer"
        
        return state