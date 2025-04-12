"""Workflow definitions for the admission process using LangGraph."""
from typing import Dict, Any, Literal, TypedDict, List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
import langgraph.graph as lg
from langgraph.graph import END, StateGraph
from agents.admission_officer import AdmissionOfficer
from agents.document_checker import DocumentChecker
from agents.shortlisting_agent import ShortlistingAgent
from agents.student_counselor import StudentCounselor
from agents.loan_agent import LoanAgent

class ApplicationStatus(BaseModel):
    """Status of a student application."""
    application_id: str
    student_name: str
    status: Literal["new", "documents_verified", "documents_rejected", 
                   "shortlisted", "rejected", "admitted", "awaiting_payment", 
                   "loan_requested", "loan_approved", "loan_rejected", 
                   "payment_completed"]
    documents: Dict[str, str] = {}
    verification_notes: Optional[str] = None
    eligibility_score: Optional[float] = None
    shortlisting_notes: Optional[str] = None
    communications: List[Dict[str, Any]] = []
    loan_details: Optional[Dict[str, Any]] = None
    payment_details: Optional[Dict[str, Any]] = None

class AdmissionState(TypedDict):
    """State for the admission workflow."""
    application: ApplicationStatus
    current_agent: str
    history: List[Dict[str, Any]]
    context: Dict[str, Any]

def initialize_agents():
    """Initialize all agents."""
    document_checker = DocumentChecker()
    shortlisting_agent = ShortlistingAgent()
    student_counselor = StudentCounselor()
    loan_agent = LoanAgent()
    admission_officer = AdmissionOfficer()
    
    return {
        "document_checker": document_checker,
        "shortlisting_agent": shortlisting_agent,
        "student_counselor": student_counselor,
        "loan_agent": loan_agent,
        "admission_officer": admission_officer,
    }

def create_admission_workflow() -> StateGraph:
    """Create the admission workflow."""
    agents = initialize_agents()
    
    # Define the workflow graph
    workflow = StateGraph(AdmissionState)
    
    # Add nodes
    workflow.add_node("document_checker", agents["document_checker"].process)
    workflow.add_node("shortlisting_agent", agents["shortlisting_agent"].process)
    workflow.add_node("student_counselor", agents["student_counselor"].process)
    workflow.add_node("loan_agent", agents["loan_agent"].process)
    workflow.add_node("admission_officer", agents["admission_officer"].process)
    
    # Define the edges
    # Start with document checking
    workflow.set_entry_point("document_checker")
    
    # After document checking, go to shortlisting agent or end if rejected
    workflow.add_conditional_edges(
        "document_checker",
        lambda state: "shortlisting_agent" if state["application"].status == "documents_verified" else END
    )
    
    # After shortlisting, go to student counselor for successful applications
    workflow.add_conditional_edges(
        "shortlisting_agent",
        lambda state: "student_counselor" if state["application"].status == "shortlisted" else END
    )
    
    # From student counselor, go to loan agent or admission officer
    workflow.add_conditional_edges(
        "student_counselor",
        lambda state: "loan_agent" if state["application"].status == "loan_requested" 
                     else "admission_officer"
    )
    
    # From loan agent, go to admission officer
    workflow.add_edge("loan_agent", "admission_officer")
    
    # Admission officer can complete the process
    workflow.add_edge("admission_officer", END)
    
    return workflow

def process_application(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a student application through the workflow."""
    # Create initial state
    application = ApplicationStatus(
        application_id=application_data["application_id"],
        student_name=application_data["student_name"],
        status="new",
        documents=application_data.get("documents", {})
    )
    
    initial_state = {
        "application": application,
        "current_agent": "document_checker",
        "history": [],
        "context": application_data.get("context", {})
    }
    
    # Create and run the workflow
    workflow = create_admission_workflow()
    workflow_app = workflow.compile()
    
    # Execute the workflow
    result = workflow_app.invoke(initial_state)
    
    return result