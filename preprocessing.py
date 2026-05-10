import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# ================= DOWNLOAD NLTK DATA =================
try:
    nltk.data.find("tokenizers/punkt")
except:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except:
    nltk.download("stopwords")

# ================= STOPWORDS =================
STOP_WORDS = set(stopwords.words("english"))

# ================= PREPROCESS TEXT =================
def preprocess_text(text):

    # Lowercase
    text = text.lower()

    # Remove symbols/numbers
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    # Tokenize
    tokens = word_tokenize(text)

    # Remove stopwords
    filtered_tokens = [
        word for word in tokens
        if word not in STOP_WORDS and len(word) > 2
    ]

    # Join back
    cleaned_text = " ".join(filtered_tokens)

    return cleaned_text.strip()