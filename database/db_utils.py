"""Database utility functions for the admission system."""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class JSONDatabase:
    """Simple JSON-based database implementation."""
    
    def __init__(self, db_path: str = "./database/data"):
        """
        Initialize the database.
        
        Args:
            db_path: Path to the database directory
        """
        self.db_path = db_path
        
        # Create database directory if it doesn't exist
        os.makedirs(db_path, exist_ok=True)
    
    def _get_collection_path(self, collection: str) -> str:
        """
        Get the path to a collection file.
        
        Args:
            collection: Collection name
        
        Returns:
            Path to the collection file
        """
        return os.path.join(self.db_path, f"{collection}.json")
    
    def _load_collection(self, collection: str) -> Dict[str, Any]:
        """
        Load a collection from disk.
        
        Args:
            collection: Collection name
        
        Returns:
            Collection data
        """
        collection_path = self._get_collection_path(collection)
        
        if not os.path.exists(collection_path):
            return {}
        
        try:
            with open(collection_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading collection {collection}: {e}")
            return {}
    
    def _save_collection(self, collection: str, data: Dict[str, Any]):
        """
        Save a collection to disk.
        
        Args:
            collection: Collection name
            data: Collection data
        """
        collection_path = self._get_collection_path(collection)
        
        try:
            with open(collection_path, 'w') as f:
                json.dump(data, f, indent=2, default=self._json_serializer)
        except Exception as e:
            logger.error(f"Error saving collection {collection}: {e}")
    
    def _json_serializer(self, obj):
        """
        Custom JSON serializer to handle datetime and Pydantic models.
        
        Args:
            obj: Object to serialize
        
        Returns:
            Serialized object
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, BaseModel):
            return obj.dict()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def insert(self, collection: str, document: Dict[str, Any]) -> str:
        """
        Insert a document into a collection.
        
        Args:
            collection: Collection name
            document: Document to insert
        
        Returns:
            Document ID
        """
        data = self._load_collection(collection)
        
        # Ensure document has an ID
        if "_id" not in document:
            from agentic_framework.utils import generate_uuid
            document["_id"] = generate_uuid()
        
        # Add document to collection
        data[document["_id"]] = document
        
        # Save collection
        self._save_collection(collection, data)
        
        return document["_id"]
    
    def insert_many(self, collection: str, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple documents into a collection.
        
        Args:
            collection: Collection name
            documents: Documents to insert
        
        Returns:
            List of document IDs
        """
        data = self._load_collection(collection)
        ids = []
        
        for document in documents:
            # Ensure document has an ID
            if "_id" not in document:
                from agentic_framework.utils import generate_uuid
                document["_id"] = generate_uuid()
            
            # Add document to collection
            data[document["_id"]] = document
            ids.append(document["_id"])
        
        # Save collection
        self._save_collection(collection, data)
        
        return ids
    
    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document in a collection.
        
        Args:
            collection: Collection name
            query: Query dictionary
        
        Returns:
            Matching document or None if not found
        """
        data = self._load_collection(collection)
        
        # Simple query matching
        for doc_id, document in data.items():
            match = True
            
            for key, value in query.items():
                if key not in document or document[key] != value:
                    match = False
                    break
            
            if match:
                return document
        
        return None
    
    def find(self, collection: str, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Find documents in a collection.
        
        Args:
            collection: Collection name
            query: Query dictionary (optional)
        
        Returns:
            List of matching documents
        """
        data = self._load_collection(collection)
        results = []
        
        if query is None:
            # Return all documents
            return list(data.values())
        
        # Simple query matching
        for doc_id, document in data.items():
            match = True
            
            for key, value in query.items():
                if key not in document or document[key] != value:
                    match = False
                    break
            
            if match:
                results.append(document)
        
        return results
    
    def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """
        Update a single document in a collection.
        
        Args:
            collection: Collection name
            query: Query dictionary
            update: Update dictionary
        
        Returns:
            True if a document was updated, False otherwise
        """
        data = self._load_collection(collection)
        
        # Find document to update
        for doc_id, document in data.items():
            match = True
            
            for key, value in query.items():
                if key not in document or document[key] != value:
                    match = False
                    break
            
            if match:
                # Update document
                for key, value in update.items():
                    document[key] = value
                
                # Save collection
                self._save_collection(collection, data)
                
                return True
        
        return False
    
    def update_many(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """
        Update multiple documents in a collection.
        
        Args:
            collection: Collection name
            query: Query dictionary
            update: Update dictionary
        
        Returns:
            Number of documents updated
        """
        data = self._load_collection(collection)
        updated_count = 0
        
        # Find documents to update
        for doc_id, document in data.items():
            match = True
            
            for key, value in query.items():
                if key not in document or document[key] != value:
                    match = False
                    break
            
            if match:
                # Update document
                for key, value in update.items():
                    document[key] = value
                
                updated_count += 1
        
        if updated_count > 0:
            # Save collection
            self._save_collection(collection, data)
        
        return updated_count
    
    def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        """
        Delete a single document from a collection.
        
        Args:
            collection: Collection name
            query: Query dictionary
        
        Returns:
            True if a document was deleted, False otherwise
        """
        data = self._load_collection(collection)
        
        # Find document to delete
        for doc_id, document in data.items():
            match = True
            
            for key, value in query.items():
                if key not in document or document[key] != value:
                    match = False
                    break
            
            if match:
                # Delete document
                del data[doc_id]
                
                # Save collection
                self._save_collection(collection, data)
                
                return True
        
        return False
    
    def delete_many(self, collection: str, query: Dict[str, Any] = None) -> int:
        """
        Delete multiple documents from a collection.
        
        Args:
            collection: Collection name
            query: Query dictionary (optional)
        
        Returns:
            Number of documents deleted
        """
        data = self._load_collection(collection)
        original_count = len(data)
        
        if query is None:
            # Delete all documents
            data = {}
            self._save_collection(collection, data)
            return original_count
        
        # Find documents to delete
        doc_ids_to_delete = []
        
        for doc_id, document in data.items():
            match = True
            
            for key, value in query.items():
                if key not in document or document[key] != value:
                    match = False
                    break
            
            if match:
                doc_ids_to_delete.append(doc_id)
        
        # Delete documents
        for doc_id in doc_ids_to_delete:
            del data[doc_id]
        
        if doc_ids_to_delete:
            # Save collection
            self._save_collection(collection, data)
        
        return len(doc_ids_to_delete)
    
    def count(self, collection: str, query: Dict[str, Any] = None) -> int:
        """
        Count documents in a collection.
        
        Args:
            collection: Collection name
            query: Query dictionary (optional)
        
        Returns:
            Number of matching documents
        """
        if query is None:
            # Count all documents
            data = self._load_collection(collection)
            return len(data)
        
        # Count matching documents
        return len(self.find(collection, query))