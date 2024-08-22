import nltk
from sentence_transformers import SentenceTransformer, util

# Download the punkt tokenizer if not already installed
nltk.download('punkt')


def has_repetitive_sentences(text, similarity_threshold=0.8):
    # Step 1: Split text into sentences
    sentences = nltk.sent_tokenize(text)

    # Step 2: Load a pre-trained sentence embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Step 3: Compute embeddings for each sentence
    embeddings = model.encode(sentences, convert_to_tensor=True)

    # Step 4: Compute similarity between each pair of sentence embeddings
    similarities = util.pytorch_cos_sim(embeddings, embeddings)

    # Step 5: Check if any similarity is above the threshold
    num_sentences = len(sentences)
    for i in range(num_sentences):
        for j in range(i + 1, num_sentences):
            if similarities[i][j] > similarity_threshold:
                return True

    return False


# Example usage
text = "This is a sentence. This is another sentence. This sentence is very similar to the first sentence."
result = has_repetitive_sentences(text, similarity_threshold=0.85)
print(result)  # Output will be True if similar sentences are found
