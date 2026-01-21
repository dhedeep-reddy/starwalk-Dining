from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings # Updated import
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import Config

class RAGPipeline:
    def __init__(self):
        # Using free local embeddings
        print("Loading HuggingFace Embeddings...")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.index_path = "faiss_index"
        self.vector_store = None
        self._load_index()

    def _load_index(self):
        if os.path.exists(self.index_path):
             try:
                self.vector_store = FAISS.load_local(self.index_path, self.embeddings, allow_dangerous_deserialization=True)
                print("Loaded vector store from disk.")
             except Exception as e:
                print(f"Failed to load index: {e}")

    def ingest_pdf(self, pdf_path):
        """
        Ingest a PDF file, split into chunks, and create a vector store.
        """
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(documents)
            
            # Create Vector Store
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            # Save to disk
            self.vector_store.save_local(self.index_path)
            return True, f"Processed {len(chunks)} chunks and saved index."
        except Exception as e:
            return False, str(e)

    def query(self, query_text):
        """
        Retrieve relevant context for a query.
        """
        if not self.vector_store:
            # Try to load again just in case
            self._load_index()
            
        if not self.vector_store:
            return "No documents processed yet."
        
        # Retrieve top 3 chunks
        docs = self.vector_store.similarity_search(query_text, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
