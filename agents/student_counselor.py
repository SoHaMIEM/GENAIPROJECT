"""Student counselor agent to communicate with students at various stages."""
from typing import Dict, Any, List
from agentic_framework.agent_base import Agent
from database.vectorstore import VectorStore

class StudentCounselor(Agent):
    """Agent responsible for communicating with students at various stages."""
    
    def __init__(self):
        """Initialize the student counselor agent."""
        system_prompt = """
        You are a Student Counselor for a university admission process.
        Your task is to handle communications with shortlisted candidates.
        
        You need to:
        1. Inform candidates about their shortlisting status
        2. Answer their queries about the admission process
        3. Guide them on the next steps (fee payment, loan application, etc.)
        4. Collect additional information if needed
        
        Always be polite, clear, and helpful in your communications.
        Provide all necessary information about deadlines, documents, and procedures.
        """
        
        super().__init__(name="Student Counselor", system_prompt=system_prompt)
        self.vector_store = VectorStore()
        
        # Load knowledge base for reference
        self.vector_store.load_knowledge_base()
    
    def generate_shortlist_notification(self, student_name: str, program: str) -> str:
        """Generate a shortlisting notification for the student."""
        # Get notification template from knowledge base
        template_info = self.vector_store.search("shortlist_notification", n_results=1)
        
        if template_info and template_info[0]["text"]:
            template = template_info[0]["text"]
            # Replace placeholders with actual data
            notification = template.replace("[STUDENT_NAME]", student_name)
            notification = notification.replace("[PROGRAM]", program)
            return notification
        
        # Default notification if template not found
        return f"""
        Dear {student_name},
        
        Congratulations! We are pleased to inform you that you have been shortlisted for the {program} program at our university.
        
        To proceed with your admission, please complete the following steps:
        1. Pay the admission fee or apply for a student loan
        2. Submit any additional documents requested
        3. Complete the online enrollment form
        
        The deadline for completing these steps is two weeks from the date of this notification.
        
        Please let us know if you have any questions or need assistance.
        
        Best regards,
        University Admissions Office
        """
    
    def handle_payment_instructions(self, student_name: str, program: str) -> str:
        """Generate payment instructions for the student."""
        # Get fee information from knowledge base
        fee_info = self.vector_store.search(f"{program} fees", n_results=1)
        
        # Default fee amount if not found
        fee_amount = 10000
        
        if fee_info:
            # Extract fee amount from information
            import re
            fee_pattern = r"fee amount: \$([\d,]+)"
            fee_match = re.search(fee_pattern, fee_info[0]["text"])
            if fee_match:
                fee_amount = int(fee_match.group(1).replace(",", ""))
        
        return f"""
        Dear {student_name},
        
        To complete your enrollment in the {program} program, please pay the admission fee of ${fee_amount}.
        
        Payment options:
        1. Online payment through the student portal
        2. Bank transfer to the university account
        3. Apply for a student loan if you need financial assistance
        
        If you wish to apply for a student loan, please let us know and we'll guide you through the process.
        
        Best regards,
        University Admissions Office
        """
    
    def handle_loan_information(self) -> str:
        """Provide information about the student loan program."""
        # Get loan information from knowledge base
        loan_info = self.vector_store.search("student loan", n_results=1)
        
        if loan_info:
            return loan_info[0]["text"]
        
        # Default loan information if not found
        return """
        Student Loan Information:
        
        Our university offers student loans to eligible candidates. To apply:
        
        1. Submit the loan application form
        2. Provide family income documentation
        3. Submit a co-signer form if required
        
        Loan eligibility depends on:
        - Academic performance
        - Financial need
        - Program of study
        
        The interest rate is 4% per annum, with repayment starting 6 months after graduation.
        
        For more information, please contact our financial aid office.
        """
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the application for student communication."""
        application = state["application"]
        
        # Only process shortlisted applications
        if application.status != "shortlisted":
            return state
        
        # Get program information from context or default to Computer Science
        program = state["context"].get("program", "Computer Science")
        
        # Generate shortlist notification
        notification = self.generate_shortlist_notification(application.student_name, program)
        
        # Add to communications
        application.communications.append({
            "type": "notification",
            "subject": "Application Shortlisted",
            "content": notification,
            "timestamp": "2023-05-15T14:30:00Z"  # In a real app, use actual timestamp
        })
        
        # Check if loan information is requested
        loan_requested = state["context"].get("loan_requested", False)
        
        if loan_requested:
            # Generate loan information
            loan_info = self.handle_loan_information()
            
            # Add to communications
            application.communications.append({
                "type": "information",
                "subject": "Student Loan Information",
                "content": loan_info,
                "timestamp": "2023-05-15T14:35:00Z"  # In a real app, use actual timestamp
            })
            
            # Update application status
            application.status = "loan_requested"
            
            # Log the action
            state["history"].append({
                "agent": self.name,
                "action": "loan_information_sent",
                "notes": "Student loan information provided"
            })
            
            # Update current agent
            state["current_agent"] = "loan_agent"
        else:
            # Generate payment instructions
            payment_info = self.handle_payment_instructions(application.student_name, program)
            
            # Add to communications
            application.communications.append({
                "type": "instruction",
                "subject": "Payment Instructions",
                "content": payment_info,
                "timestamp": "2023-05-15T14:32:00Z"  # In a real app, use actual timestamp
            })
            
            # Update application status
            application.status = "awaiting_payment"
            
            # Log the action
            state["history"].append({
                "agent": self.name,
                "action": "payment_instructions_sent",
                "notes": "Payment instructions sent to student"
            })
            
            # Update current agent
            state["current_agent"] = "admission_officer"
        
        return state