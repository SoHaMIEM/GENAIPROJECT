"""Admission officer to oversee the entire admission process."""
from typing import Dict, Any, List
from agentic_framework.agent_base import Agent
from database.vectorstore import VectorStore

class AdmissionOfficer(Agent):
    """Agent responsible for overseeing the entire admission process."""
    
    def __init__(self):
        """Initialize the admission officer agent."""
        system_prompt = """
        You are the Admission Officer for a university.
        Your task is to oversee the entire admission process.
        
        You need to:
        1. Monitor the progress of applications through various stages
        2. Make final admission decisions
        3. Generate admission letters and fee slips
        4. Handle special cases and exceptions
        
        You have the authority to override decisions made by other agents if necessary.
        Always ensure the admission process follows university policies and is fair to all applicants.
        """
        
        super().__init__(name="Admission Officer", system_prompt=system_prompt)
        self.vector_store = VectorStore()
        
        # Load knowledge base for reference
        self.vector_store.load_knowledge_base()
    
    def generate_admission_letter(self, student_name: str, program: str) -> str:
        """Generate an admission letter for the student."""
        # Get template from knowledge base
        template_info = self.vector_store.search("admission_letter", n_results=1)
        
        if template_info and template_info[0]["text"]:
            template = template_info[0]["text"]
            # Replace placeholders with actual data
            letter = template.replace("[STUDENT_NAME]", student_name)
            letter = letter.replace("[PROGRAM]", program)
            return letter
        
        # Default letter if template not found
        return f"""
        Dear {student_name},
        
        Congratulations! It is with great pleasure that we offer you admission to the {program} program at our university.
        
        This letter confirms your place in the program starting in the Fall 2023 semester.
        
        To secure your spot, please:
        1. Accept this offer within 10 days
        2. Complete the enrollment process
        3. Pay the required fees or confirm your loan approval
        
        We look forward to welcoming you to our campus.
        
        Sincerely,
        University Admissions Office
        """
    
    def generate_fee_slip(self, student_name: str, program: str) -> str:
        """Generate a fee slip for the student."""
        # Get fee information from knowledge base
        fee_info = self.vector_store.search(f"{program} fees", n_results=1)
        
        # Default fee structure if not found
        tuition_fee = 10000
        registration_fee = 500
        facility_fee = 1500
        total_fee = tuition_fee + registration_fee + facility_fee
        
        if fee_info:
            # Extract fee details from information
            import re
            tuition_pattern = r"tuition fee: \$([\d,]+)"
            tuition_match = re.search(tuition_pattern, fee_info[0]["text"])
            if tuition_match:
                tuition_fee = int(tuition_match.group(1).replace(",", ""))
            
            registration_pattern = r"registration fee: \$([\d,]+)"
            registration_match = re.search(registration_pattern, fee_info[0]["text"])
            if registration_match:
                registration_fee = int(registration_match.group(1).replace(",", ""))
            
            facility_pattern = r"facility fee: \$([\d,]+)"
            facility_match = re.search(facility_pattern, fee_info[0]["text"])
            if facility_match:
                facility_fee = int(facility_match.group(1).replace(",", ""))
            
            total_fee = tuition_fee + registration_fee + facility_fee
        
        # Get template from knowledge base
        template_info = self.vector_store.search("fee_slip", n_results=1)
        
        if template_info and template_info[0]["text"]:
            template = template_info[0]["text"]
            # Replace placeholders with actual data
            slip = template.replace("[STUDENT_NAME]", student_name)
            slip = slip.replace("[PROGRAM]", program)
            slip = slip.replace("[TUITION_FEE]", f"${tuition_fee:,}")
            slip = slip.replace("[REGISTRATION_FEE]", f"${registration_fee:,}")
            slip = slip.replace("[FACILITY_FEE]", f"${facility_fee:,}")
            slip = slip.replace("[TOTAL_FEE]", f"${total_fee:,}")
            return slip
        
        # Default fee slip if template not found
        return f"""
        UNIVERSITY FEE SLIP
        
        Student: {student_name}
        Program: {program}
        Term: Fall 2023
        
        Fee Details:
        - Tuition Fee: ${tuition_fee:,}
        - Registration Fee: ${registration_fee:,}
        - Facility Fee: ${facility_fee:,}
        
        Total Amount Due: ${total_fee:,}
        
        Payment Deadline: June 30, 2023
        
        Payment Methods:
        - Online through student portal
        - Bank transfer to University account
        - Check payable to University
        
        Please include your student ID with all payments.
        """
    
    def finalize_admission(self, application: Dict[str, Any], program: str) -> Dict[str, Any]:
        """Finalize the admission process for the student."""
        # Generate admission letter
        admission_letter = self.generate_admission_letter(application.student_name, program)
        
        # Add to communications
        application.communications.append({
            "type": "letter",
            "subject": "Admission Letter",
            "content": admission_letter,
            "timestamp": "2023-05-25T09:00:00Z"  # In a real app, use actual timestamp
        })
        
        # Generate fee slip
        fee_slip = self.generate_fee_slip(application.student_name, program)
        
        # Add to communications
        application.communications.append({
            "type": "document",
            "subject": "Fee Slip",
            "content": fee_slip,
            "timestamp": "2023-05-25T09:05:00Z"  # In a real app, use actual timestamp
        })
        
        # Update application status
        application.status = "admitted"
        
        return application
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the application for final admission decision."""
        application = state["application"]
        
        # Get program information from context or default to Computer Science
        program = state["context"].get("program", "Computer Science")
        
        # Handle different application statuses
        if application.status == "awaiting_payment":
            # In a real system, check if payment has been received
            # For this demo, assume payment is complete
            application.payment_details = {
                "amount_paid": 12000,
                "payment_method": "Online",
                "payment_date": "2023-05-22T14:30:00Z",
                "transaction_id": "TRX12345678"
            }
            
            application.status = "payment_completed"
            
            # Log the payment
            state["history"].append({
                "agent": self.name,
                "action": "payment_received",
                "amount": application.payment_details["amount_paid"],
                "notes": "Payment received and processed"
            })
        
        if application.status in ["payment_completed", "loan_approved"]:
            # Finalize admission
            application = self.finalize_admission(application, program)
            
            # Log the admission
            state["history"].append({
                "agent": self.name,
                "action": "admission_finalized",
                "notes": "Admission letter and fee slip generated"
            })
        
        if application.status == "loan_rejected":
            # Handle loan rejection by giving the student another chance to pay directly
            payment_reminder = f"""
            Dear {application.student_name},
            
            We understand that your loan application was not approved. However, you still have the opportunity
            to secure your admission by making a direct payment.
            
            Please log into the student portal to view payment options or contact our financial aid office
            to discuss alternative financial assistance programs.
            
            Best regards,
            University Admissions Office
            """
            
            # Add to communications
            application.communications.append({
                "type": "letter",
                "subject": "Payment Reminder",
                "content": payment_reminder,
                "timestamp": "2023-05-25T14:00:00Z"  # In a real app, use actual timestamp
            })
            
            # Update application status
            application.status = "awaiting_payment"
            
            # Log the action
            state["history"].append({
                "agent": self.name,
                "action": "payment_reminder_sent",
                "notes": "Payment reminder sent after loan rejection"
            })
        
        return state