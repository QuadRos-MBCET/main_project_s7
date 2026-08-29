import numpy as np
import os

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

# Seed Exemplars for FAISS database indexing
EXEMPLARS = [
    {"title": "Mega Casino Win Cash", "caption": "Spin the jackpot slot machine and win real cash prize tonight.", "policy": "Gambling", "decision": "rejected"},
    {"title": "Weekend Brews and Draft Beer", "caption": "Join us at the local pub for discount wine and whiskey drinks.", "policy": "Alcohol/Tobacco", "decision": "under_review"},
    {"title": "Action Combat: Blood and Guns", "caption": "Watch the ultimate sword fighting combat trailer with weapons.", "policy": "Violence", "decision": "rejected"},
    {"title": "Adult Date Matchmaker", "caption": "Find singles in your city. Erotic chat for adults 18+.", "policy": "Adult/Sexual Content", "decision": "rejected"},
    {"title": "Guaranteed Returns Paisa Double Scheme", "caption": "Earn cash fast with zero risk. Click to join our giveaway scheme.", "policy": "Misleading Advertisement", "decision": "rejected"},
    {"title": "Learn Python Code Basics", "caption": "Step by step tutorials for programmers and beginners.", "policy": "None", "decision": "approved"},
    {"title": "Fresh Organic Apples Store", "caption": "Locally grown organic fruits delivered directly to your doorstep.", "policy": "None", "decision": "approved"}
]

# Simple Bag-of-Words / TF-IDF Vectorizer built in Pure Python/NumPy to keep it fast and compatible
class LightweightVectorizer:
    def __init__(self):
        self.vocabulary = {}
        
    def fit(self, texts):
        unique_words = set()
        for text in texts:
            words = self._tokenize(text)
            unique_words.update(words)
        self.vocabulary = {word: i for i, word in enumerate(sorted(unique_words))}
        
    def _tokenize(self, text):
        return [w.strip() for w in text.lower().replace(",", " ").replace(".", " ").replace("!", " ").split() if len(w.strip()) > 2]
        
    def transform(self, texts):
        dim = len(self.vocabulary)
        if dim == 0:
            return np.zeros((len(texts), 1), dtype=np.float32)
        vectors = []
        for text in texts:
            vec = np.zeros(dim, dtype=np.float32)
            words = self._tokenize(text)
            for w in words:
                if w in self.vocabulary:
                    vec[self.vocabulary[w]] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec)
        return np.array(vectors, dtype=np.float32)

# Initialize vectorizer
vectorizer = LightweightVectorizer()
texts = [f"{ex['title']} {ex['caption']}" for ex in EXEMPLARS]
vectorizer.fit(texts)
exemplar_vectors = vectorizer.transform(texts)

# Build Index
if HAS_FAISS:
    dim = exemplar_vectors.shape[1]
    # Use IndexFlatL2 (Euclidean distance search) or IndexFlatIP (Inner product)
    faiss_index = faiss.IndexFlatL2(dim)
    faiss_index.add(exemplar_vectors)
else:
    faiss_index = None

def search_similar_exemplar(query_text: str) -> dict:
    """
    Queries the FAISS index to find the nearest matching historical policy exemplar.
    Includes a pure numpy fallback for WebAssembly browser executions.
    """
    query_vector = vectorizer.transform([query_text])
    
    if HAS_FAISS and faiss_index is not None:
        # Search the index
        distances, indices = faiss_index.search(query_vector, 1)
        best_idx = indices[0][0]
        best_dist = float(distances[0][0])
    else:
        # Fallback cosine similarity matrix multiplication
        similarities = np.dot(exemplar_vectors, query_vector.T).flatten()
        best_idx = int(np.argmax(similarities))
        # Convert similarity to a distance proxy (1 - cosine similarity)
        best_dist = float(1.0 - similarities[best_idx])
        
    if 0 <= best_idx < len(EXEMPLARS):
        match = EXEMPLARS[best_idx]
        return {
            "title": match["title"],
            "caption": match["caption"],
            "policy": match["policy"],
            "decision": match["decision"],
            "distance": round(best_dist, 4)
        }
    return None

if __name__ == "__main__":
    test_query = "casino slot win cash prize"
    res = search_similar_exemplar(test_query)
    print(f"FAISS Status: {'Running CPU-Native' if HAS_FAISS else 'Running Browser WebAssembly Fallback'}")
    print(f"Query text  : '{test_query}'")
    print(f"Match Found : '{res['title']}' (Violes policy: {res['policy']})")
    print(f"Distance    : {res['distance']}")
