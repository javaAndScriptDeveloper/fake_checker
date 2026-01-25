import numpy as np
from sklearn.naive_bayes import MultinomialNB

from processors.clickbait_title.features import top_30_words, stop_words, lexical, pos_tags, interpunction, \
    avg_char_num, ttr_normalized, num_words, long_words, q_words_counts
from processors.clickbait_title.helpers import get_data


def prepare_model():
    """Prepares and trains the clickbait detection model."""
    # Load dataset
    non_clickbait = "processors/clickbait_title/non_clickbait_data.txt"
    clickbait = "processors/clickbait_title/clickbait_data.txt"

    non_clickbait_headlines = get_data(non_clickbait)
    clickbait_headlines = get_data(clickbait)
    all_headlines = non_clickbait_headlines + clickbait_headlines

    non_cb_labels = [0] * len(non_clickbait_headlines)
    cb_labels = [1] * len(clickbait_headlines)
    all_labels = non_cb_labels + cb_labels

    # Extract and store top words for consistency
    top_words = top_30_words(all_headlines)

    # Extract features for training
    all_features = np.concatenate(
        (
            stop_words(all_headlines),
            pos_tags(all_headlines),
            lexical(all_headlines, top_words),
            interpunction(all_headlines),
            np.array(avg_char_num(all_headlines)).reshape(len(all_headlines), 1),
            np.array(ttr_normalized(all_headlines)).reshape(len(all_headlines), 1),
            np.array(num_words(all_headlines)).reshape(len(all_headlines), 1),
            np.array(long_words(all_headlines)).reshape(len(all_headlines), 1),
            q_words_counts(all_headlines),
        ),
        axis=1,
    )

    # Train Naive Bayes classifier
    model = MultinomialNB()
    model.fit(all_features, all_labels)

    return model, top_words


# Lazy load model - only prepare when needed
_model = None
_top_words = None


def _get_model():
    """Get or create the model (lazy loading)."""
    global _model, _top_words
    if _model is None:
        _model, _top_words = prepare_model()
    return _model, _top_words


def is_clickbait(text):
    """Determines if a given text is clickbait using the trained model."""
    model, top_words = _get_model()
    
    # Extract features for input text using the same top words
    text_features = np.concatenate(
        (
            stop_words([text]),
            pos_tags([text]),
            lexical([text], top_words),
            interpunction([text]),
            np.array(avg_char_num([text])).reshape(1, 1),
            np.array(ttr_normalized([text])).reshape(1, 1),
            np.array(num_words([text])).reshape(1, 1),
            np.array(long_words([text])).reshape(1, 1),
            q_words_counts([text]),
        ),
        axis=1,
    )

    return model.predict(text_features)