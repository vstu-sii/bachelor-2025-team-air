import faiss
import pickle
from sentence_transformers import SentenceTransformer
from preprocessing.clean_text import clean_text
import os

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

class ResumeVectorStore:
    def __init__(self, index_path):
        self.index = faiss.read_index(os.path.join(index_path, "resume_index.faiss"))
        self.data = pickle.load(open(os.path.join(index_path, "resume_data.pkl"), "rb"))
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def search(self, query_text, top_k=30):
        query_text = clean_text(query_text)
        q_vec = self.model.encode([query_text])
        distances, ids = self.index.search(q_vec, top_k)
        results = [self.data.iloc[i].to_dict() for i in ids[0]]
        return results
