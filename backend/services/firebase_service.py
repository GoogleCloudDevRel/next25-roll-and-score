import logging

import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)


class FirestoreService:
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.info("Creating new FirestoreService instance")
            cls._instance = super().__new__(cls)
            cls._instance.db = None
        else:
            logger.info("Using existing FirestoreService instance")
        return cls._instance

    def __init__(self, database_id: str):
        if self.db is None:
            try:
                self.db = self.initialize_firestore(database_id)
            except Exception as e:
                logger.error(f"Error initializing Firestore: {e}")
                self.db = None  # to prevent further errors, set db to none.
        else:
            logger.info(f"{self.__class__.__name__}: __init__ skipped because instance already initialized")

    def initialize_firestore(self, database_id: str):
        try:
            if not firebase_admin._apps:  # Initialize only once
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
            return firestore.client(database_id=database_id)
        except Exception as e:
            logger.error(f"Error initializing Firestore client: {e}")
            raise

    def create_doc(self, collection_name, document_id=None, data={}):
        """
        Creates a document in Firestore. If document_id is None, Firestore auto-generates one.
        """
        if self.db:
            try:
                if document_id:
                    doc_ref = self.db.collection(collection_name).document(document_id)
                    doc_ref.set(data)
                    logger.info(f"Document: {document_id} exists in collection: {collection_name}. Updated it with data: {data}.")
                    return document_id
                else:
                    doc_ref = self.db.collection(collection_name).document()
                    doc_ref.set(data)
                    logger.info(f"Created a new document: {doc_ref.id} in collection: {collection_name} with data: {data}")
                    return doc_ref.id
            except Exception as e:
                logger.error(f"Unable to create a new document in collection: {collection_name}. Error: {e}")
                raise e
        else:
            raise Exception("Firestore not initialized")

    def get_doc(self, collection_name, document_id):
        """
        Retrieves a document from Firestore.
        """
        if self.db:
            try:
                doc_ref = self.db.collection(collection_name).document(document_id)
                doc = doc_ref.get()
                if doc.exists:
                    return doc.to_dict()
                else:
                    return None
            except Exception as e:
                raise e
        else:
            raise Exception("Firestore not initialized")

    def get_field(self, collection_name, document_id, field_name):
        """
        Retrieves a specific field from a Firestore document.
        """
        if self.db:
            try:
                doc_ref = self.db.collection(collection_name).document(document_id)
                doc = doc_ref.get()
                if doc.exists:
                    doc_dict = doc.to_dict()
                    if field_name in doc_dict:
                        return doc_dict[field_name]
                    else:
                        return None  # Field does not exist
                else:
                    return None  # Document does not exist
            except Exception as e:
                logger.error(f"Error retrieving field {field_name} from document {document_id}: {e}")
                raise e
        else:
            raise Exception("Firestore not initialized")

    def get_top_n_by_score(self, collection_name, score_field="totalScore", n=5):
        """
        Retrieves the top 'n' documents from a collection, ordered by 'score_field' in descending order.
        """
        if self.db:
            try:
                query = self.db.collection(collection_name).order_by(score_field, direction=firestore.Query.DESCENDING).limit(n)
                results = query.stream()
                top_scores = []
                for doc in results:
                    top_scores.append(doc.to_dict()['totalScore'])
                return top_scores
            except Exception as e:
                logger.error(f"Error retrieving top {n} scores from {collection_name}: {e}")
                raise e
        else:
            raise Exception("Firestore not initialized")

    def update_field(self, collection_name, document_id, field_name, field_value):
        """
        Updates a specific field in a Firestore document.
        """
        if self.db:
            try:
                doc_ref = self.db.collection(collection_name).document(document_id)
                doc_ref.update({field_name: field_value})
                logger.info(f"Updated {field_name} with value {field_value}")
            except Exception as e:
                logger.error(f"Error updating {field_name} with value {field_value}")
                raise e
        else:
            raise Exception("Firestore not initialized")

    def add_item_to_list(self, collection_name, document_id, list_field_name, item):
        """
        Adds an item to a list field in a Firestore document.
        """
        if self.db:
            try:
                doc_ref = self.db.collection(collection_name).document(document_id)
                doc_ref.update({list_field_name: firestore.ArrayUnion([item])})
                logger.info(f"Added {item} to score list from document: {document_id}")
            except Exception as e:
                logger.error(f"Error adding {item} to score list from document: {document_id}")
                raise e
        else:
            raise Exception("Firestore not initialized")
