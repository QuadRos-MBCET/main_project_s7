import numpy as np

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

EXEMPLARS = [
    {"title": "Mega Casino Win Cash", "caption": "Spin jackpot slot machine win real cash prize tonight.", "policy": "Gambling", "decision": "UNSAFE_FOR_ALL"},
    {"title": "Weekend Brews and Draft Beer", "caption": "Join us at the pub for discount wine and whiskey drinks.", "policy": "Alcohol/Tobacco", "decision": "AGE_18_PLUS"},
    {"title": "Action Combat Blood and Guns", "caption": "Watch ultimate sword fighting combat trailer with weapons.", "policy": "Violence", "decision": "UNSAFE_FOR_ALL"},
    {"title": "Adult Date Matchmaker", "caption": "Find singles in your city. Erotic chat for adults 18+.", "policy": "Adult/Sexual Content", "decision": "AGE_18_PLUS"},
    {"title": "Guaranteed Returns Paisa Double Scheme", "caption": "Earn cash fast with zero risk giveaway scheme.", "policy": "Misleading Advertisement", "decision": "UNSAFE_FOR_ALL"},
    {"title": "Learn Python Code Basics", "caption": "Step by step tutorials for programmers and beginners.", "policy": "None", "decision": "SAFE_FOR_ALL"},
    {"title": "Fresh Organic Apples Store", "caption": "Locally grown organic fruits delivered directly to your doorstep.", "policy": "None", "decision": "SAFE_FOR_ALL"}
]

class LightweightVectorizer:
    def __init__(self):
        self.vocab = {}
        
    def fit(self, texts):
        words = set()
        for t in texts:
            for w in t.lower().replace(",", " ").replace(".", " ").split():
                if len(w.strip()) > 2:
                    words.add(w.strip())
        self.vocab = {w: i for i, w in enumerate(sorted(words))}
        
    def transform(self, texts):
        dim = len(self.vocab)
        if dim == 0:
            return np.zeros((len(texts), 1), dtype=np.float32)
        vecs = []
        for t in texts:
            vec = np.zeros(dim, dtype=np.float32)
            for w in t.lower().replace(",", " ").replace(".", " ").split():
                w = w.strip()
                if w in self.vocab:
                    vec[self.vocab[w]] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            vecs.append(vec)
        return np.array(vecs, dtype=np.float32)

vectorizer = LightweightVectorizer()
raw_texts = [f"{e['title']} {e['caption']}" for e in EXEMPLARS]
vectorizer.fit(raw_texts)
exemplar_vectors = vectorizer.transform(raw_texts)

if HAS_FAISS:
    dim = exemplar_vectors.shape[1]
    faiss_index = faiss.IndexFlatL2(dim)
    faiss_index.add(exemplar_vectors)
else:
    faiss_index = None

def retrieve_similar_exemplar(query_text: str) -> dict:
    """
    Queries FAISS vector index to retrieve the nearest annotated historical policy case.
    """
    query_vec = vectorizer.transform([query_text])
    
    if HAS_FAISS and faiss_index is not None:
        distances, indices = faiss_index.search(query_vec, 1)
        best_idx = indices[0][0]
        best_dist = float(distances[0][0])
    else:
        sims = np.dot(exemplar_vectors, query_vec.T).flatten()
        best_idx = int(np.argmax(sims))
        best_dist = float(1.0 - sims[best_idx])
        
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
