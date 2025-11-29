import os
import pickle
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from preprocessing.clean_text import clean_text

EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # можно поменять

def build_embeddings():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "data", "resume_dataset_fixed.csv")          # ваш готовый CSV
    index_path = "../data/faiss_index"
    processed_csv_path = "../data/processed.csv"

    os.makedirs(index_path, exist_ok=True)

    df = pd.read_csv(csv_path)

    df['combined_text'] = df.apply(
        lambda row: " ".join([str(row[col]) for col in ['summary','skills','experience'] if col in row]),
        axis=1
    )
    df['combined_text'] = df['combined_text'].apply(clean_text)

    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(df['combined_text'].tolist(), convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, os.path.join(index_path, "resume_index.faiss"))
    pickle.dump(df, open(os.path.join(index_path, "resume_data.pkl"), "wb"))
    df.to_csv(processed_csv_path, index=False)

    print(f"Embeddings и FAISS индекс созданы: {index_path}")
