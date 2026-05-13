import re
import nltk
import os

# 1. SETUP LOCAL PATH (The "Anti-Error" Fix)
# This creates a folder inside your app to store NLTK data
nltk_data_path = os.path.join(os.getcwd(), 'nltk_data')
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)
nltk.data.path.append(nltk_data_path)

# 2. DOWNLOAD RESOURCES
# We include 'punkt_tab' which is required by newer NLTK versions
resources = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']

for res in resources:
    try:
        nltk.download(res, download_dir=nltk_data_path, quiet=True)
    except Exception as e:
        print(f"NLTK Download Warning: {e}")

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Initialize Lemmatizer (Matches your Conceptual Framework Figure 1)
lemmatizer = WordNetLemmatizer()

# Ensure Stopwords are loaded properly
try:
    STOP_WORDS = set(stopwords.words("english"))
except:
    STOP_WORDS = set()

def preprocess_text(text):
    if not text:
        return ""

    # Lowercase and remove non-alphabet symbols [cite: 237, 252]
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    
    # TOKENIZATION with Fallback (The "Cry-Proof" logic)
    try:
        tokens = word_tokenize(text)
    except:
        # If NLTK fails, we use a simple split so the app keeps running!
        tokens = text.split()
    
    # LEMMATIZATION [cite: 58, 215]
    # Reduces words like "developing" and "developed" to "develop"
    cleaned_tokens = [
        lemmatizer.lemmatize(word) 
        for word in tokens 
        if word not in STOP_WORDS and len(word) > 2
    ]
    
    return " ".join(cleaned_tokens).strip()