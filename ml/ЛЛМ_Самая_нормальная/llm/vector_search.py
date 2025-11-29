import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import pickle
import os


class VectorSearch:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.candidates = []

    def build_index(self, candidates):
        """Строит индекс для быстрого поиска"""
        print("🔨 Строим векторный индекс...")
        self.candidates = candidates

        # Создаем эмбеддинги
        texts = [c.get('combined_text', '') for c in candidates]
        embeddings = self.model.encode(texts, show_progress_bar=True)

        # Создаем FAISS индекс
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # cosine similarity

        # Нормализуем векторы для cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))

        print(f"✅ Индекс построен: {len(candidates)} кандидатов")

    def save_index(self, path='data/faiss_index'):
        """Сохраняет индекс"""
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, f"{path}/index.faiss")
        with open(f"{path}/candidates.pkl", 'wb') as f:
            pickle.dump(self.candidates, f)
        print(f"💾 Индекс сохранен в {path}")

    def load_index(self, path='data/faiss_index'):
        """Загружает индекс"""
        self.index = faiss.read_index(f"{path}/index.faiss")
        with open(f"{path}/candidates.pkl", 'rb') as f:
            self.candidates = pickle.load(f)
        print(f"📂 Индекс загружен: {len(self.candidates)} кандидатов")

    def search(self, query, top_k=50):
        """Быстрый поиск похожих кандидатов"""
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)

        # Ищем top_k похожих
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.candidates):
                results.append({
                    "candidate": self.candidates[idx],
                    "score": float(score)
                })

        return results