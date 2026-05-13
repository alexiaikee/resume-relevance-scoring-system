import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required data
for resource in ["punkt", "stopwords", "wordnet", "omw-1.4"]:
    try:
        nltk.data.find(f"corpora/{resource}")
    except:
        nltk.download(resource)

STOP_WORDS = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    # Lowercase and remove symbols
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords and Lemmatize
    cleaned_tokens = [
        lemmatizer.lemmatize(word) 
        for word in tokens 
        if word not in STOP_WORDS and len(word) > 2
    ]
    
    return " ".join(cleaned_tokens)