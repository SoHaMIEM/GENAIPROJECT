"""Document checking agent to validate submitted applications and documents."""
from typing import Dict, Any
import os
import re
from PyPDF2 import PdfReader
from docx import Document
from agentic_framework.agent_base import Agent
from database.vectorstore import VectorStore

class DocumentChecker(Agent):
    """Agent responsible for validating submitted applications and documents."""
    
    def __init__(self):
        """Initialize the document checking agent."""
        system_prompt = """
        You are a Document Verification Agent for a university admission process.
        Your task is to carefully verify all the documents submitted by applicants.
        
        You need to check:
        1. If all required documents are submitted
        2. If the documents are properly formatted and legible
        3. If the academic credentials meet the minimum requirements
        4. If there are any discrepancies or inconsistencies in the documents
        
        Required documents:
        - Completed application form
        - Academic transcripts
        - ID/Passport
        - Recommendation letters
        - Statement of purpose
        
        Be thorough in your verification process. Flag any issues or missing documents.
        If documents are incomplete or have issues, reject them and provide clear reasons.
        If all documents are valid, mark them as verified.
        """
        
        super().__init__(name="Document Checker", system_prompt=system_prompt)
        self.vector_store = VectorStore()
        
        # Load knowledge base for reference
        self.vector_store.load_knowledge_base()
        
        # Load required documents list
        self.required_documents = [
            "application_form",
            "academic_transcripts",
            "id_passport",
            "recommendation_letters",
            "statement_of_purpose"
        ]
    
    def extract_text_from_document(self, document_path: str) -> str:
        """Extract text from a document file."""
        if document_path.endswith(".pdf"):
            reader = PdfReader(document_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        
        elif document_path.endswith(".docx"):
            doc = Document(document_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        elif document_path.endswith(".txt"):
            with open(document_path, "r") as f:
                return f.read()
        
        return "Unsupported document format"
    
    def check_document_completeness(self, documents: Dict[str, str]) -> Dict[str, bool]:
        """Check if all required documents are present."""
        completeness = {}
        
        for doc_type in self.required_documents:
            completeness[doc_type] = doc_type in documents
            
        return completeness
    
    def validate_academic_credentials(self, transcript_text: str) -> Dict[str, Any]:
        """Validate academic credentials from transcript."""
        # Extract GPA using regex
        gpa_pattern = r"GPA:\s*([\d.]+)"
        gpa_match = re.search(gpa_pattern, transcript_text)
        gpa = float(gpa_match.group(1)) if gpa_match else None
        
        # Validate credentials based on eligibility criteria
        eligibility_info = self.vector_store.search("eligibility criteria", n_results=1)
        min_gpa_required = 3.0  # Default value
        
        if eligibility_info:
            # Extract min GPA from eligibility information
            min_gpa_pattern = r"minimum GPA of ([\d.]+)"
            min_gpa_match = re.search(min_gpa_pattern, eligibility_info[0]["text"])
            if min_gpa_match:
                min_gpa_required = float(min_gpa_match.group(1))
        
        is_valid = gpa is not None and gpa >= min_gpa_required
        
        return {
            "gpa": gpa,
            "min_gpa_required": min_gpa_required,
            "is_valid": is_valid
        }
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the application documents."""
        application = state["application"]
        documents = application.documents
        
        # Check document completeness
        completeness = self.check_document_completeness(documents)
        all_documents_present = all(completeness.values())
        
        if not all_documents_present:
            missing_docs = [doc for doc, present in completeness.items() if not present]
            verification_notes = f"Missing documents: {', '.join(missing_docs)}"
            
            # Update application status
            application.status = "documents_rejected"
            application.verification_notes = verification_notes
            
            # Log the rejection
            state["history"].append({
                "agent": self.name,
                "action": "document_rejection",
                "reason": verification_notes
            })
            
            return state
        
        # Simulate document content extraction
        # In a real system, this would extract text from actual uploaded documents
        transcript_text = "Student Academic Record\nGPA: 3.5\nMajor: Computer Science"
        
        # Validate academic credentials
        credentials_result = self.validate_academic_credentials(transcript_text)
        
        if not credentials_result["is_valid"]:
            verification_notes = f"Academic credentials do not meet requirements. GPA: {credentials_result['gpa']}, Required GPA: {credentials_result['min_gpa_required']}"
            
            # Update application status
            application.status = "documents_rejected"
            application.verification_notes = verification_notes
            
            # Log the rejection
            state["history"].append({
                "agent": self.name,
                "action": "document_rejection",
                "reason": verification_notes
            })
            
            return state
        
        # All documents are valid
        verification_notes = "All documents verified successfully."
        
        # Update application status
        application.status = "documents_verified"
        application.verification_notes = verification_notes
        application.eligibility_score = credentials_result["gpa"]
        
        # Log the verification
        state["history"].append({
            "agent": self.name,
            "action": "document_verification",
            "result": "success",
            "notes": verification_notes
        })
        
        # Update current agent
        state["current_agent"] = "shortlisting_agent"
        
        return state