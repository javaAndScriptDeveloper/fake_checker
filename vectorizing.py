import numpy as np
from sentence_transformers import SentenceTransformer

sbert_model = SentenceTransformer('bert-base-nli-mean-tokens')

sentences = ["I ate dinner.",
             "We had a three-course meal.",
             "Brad came to dinner with us.",
             "He loves fish tacos.",
             "In the end, we all felt like we ate too much.",
             "We all agreed; it was a magnificent evening."]

sentence_embeddings = sbert_model.encode(sentences)

query = "I had pizza and pasta"
query_vec = sbert_model.encode([query])[0]

def cosine(u, v):
    return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))

for sent in sentences:
  print(query_vec)
  sim = cosine(query_vec, sbert_model.encode([sent])[0])
  print("Sentence = ", sent, "; similarity = ", sim)
