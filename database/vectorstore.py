"""Vector store setup and operations using ChromaDB."""
import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import pandas as pd

class VectorStore:
    """Vector store for document retrieval and similarity search."""
    
    def __init__(self, collection_name: str = "admission_documents"):
        """Initialize the vector store."""
        # Set up ChromaDB client
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./database/chroma_db"
        ))
        
        # Set up embedding function
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
        except ValueError:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents with id, text, and metadata
        """
        ids = [doc["id"] for doc in documents]
        texts = [doc["text"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query.
        
        Args:
            query: Search query
            n_results: Number of results to return
        
        Returns:
            List of matching documents
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return [
            {
                "id": id,
                "text": document,
                "metadata": metadata,
                "distance": distance
            }
            for id, document, metadata, distance in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
    
    def load_knowledge_base(self):
        """Load knowledge base documents into the vector store."""
        knowledge_base_dir = "./knowledge_base"
        documents = []
        
        # Get all files in the knowledge base directory
        for filename in os.listdir(knowledge_base_dir):
            if filename.endswith(".md"):
                file_path = os.path.join(knowledge_base_dir, filename)
                with open(file_path, "r") as f:
                    content = f.read()
                
                doc_id = filename.replace(".md", "")
                documents.append({
                    "id": doc_id,
                    "text": content,
                    "metadata": {"source": filename, "type": "knowledge_base"}
                })
        
        if documents:
            self.add_documents(documents)
            print(f"Loaded {len(documents)} documents into the vector store.")
    
    def save_applications(self, applications: List[Dict[str, Any]]):
        """Save application data to the vector store."""
        documents = []
        
        for app in applications:
            app_id = app["application_id"]
            # Convert app data to text format
            text = f"Application ID: {app_id}\n"
            text += f"Student Name: {app['student_name']}\n"
            text += f"Status: {app['status']}\n"
            
            # Add other application details
            for key, value in app.items():
                if key not in ["application_id", "student_name", "status"]:
                    text += f"{key}: {value}\n"
            
            documents.append({
                "id": f"application_{app_id}",
                "text": text,
                "metadata": {"type": "application", "status": app["status"]}
            })
        
        if documents:
            self.add_documents(documents)
            print(f"Saved {len(documents)} applications to the vector store.")
    
    def get_applications_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get applications with a specific status."""
        results = self.collection.get(
            where={"type": "application", "status": status}
        )
        
        return results

    def update_application_status(self, application_id: str, new_status: str):
        """Update the status of an application."""
        # Get the existing application
        results = self.collection.get(
            ids=[f"application_{application_id}"]
        )
        
        if not results["ids"]:
            print(f"Application {application_id} not found.")
            return
        
        # Update the application
        old_metadata = results["metadatas"][0]
        old_metadata["status"] = new_status
        
        self.collection.update(
            ids=[f"application_{application_id}"],
            metadatas=[old_metadata]
        )
        
        print(f"Updated application {application_id} status to {new_status}.")