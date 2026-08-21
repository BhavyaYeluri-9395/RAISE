# test_setup.py
print("=" * 50)
print("Testing Smart Resume Screener Setup")
print("=" * 50)

# Test 1: spaCy
print("\n1. Testing spaCy...")
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    print("✅ spaCy loaded successfully!")
except Exception as e:
    print(f"❌ spaCy error: {e}")

# Test 2: PyMuPDF
print("\n2. Testing PyMuPDF...")
try:
    import fitz
    print("✅ PyMuPDF loaded successfully!")
except Exception as e:
    print(f"❌ PyMuPDF error: {e}")

# Test 3: skills package
print("\n3. Testing skills package...")
try:
    import skills
    print("✅ skills package loaded successfully!")
except Exception as e:
    print(f"❌ skills package error: {e}")

# Test 4: sentence-transformers
print("\n4. Testing sentence-transformers...")
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ sentence-transformers loaded successfully!")
except Exception as e:
    print(f"❌ sentence-transformers error: {e}")

# Test 5: Gemini
print("\n5. Testing Gemini API...")
try:
    import google.generativeai as genai
    import os
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_actual_api_key_here":
        genai.configure(api_key=api_key)
        print("✅ Gemini API key found and configured!")
    else:
        print("⚠️ Gemini API key not found. Please add to .env file")
except Exception as e:
    print(f"❌ Gemini error: {e}")

# Test 6: FastAPI
print("\n6. Testing FastAPI...")
try:
    import fastapi
    print("✅ FastAPI loaded successfully!")
except Exception as e:
    print(f"❌ FastAPI error: {e}")

# Test 7: Streamlit
print("\n7. Testing Streamlit...")
try:
    import streamlit
    print("✅ Streamlit loaded successfully!")
except Exception as e:
    print(f"❌ Streamlit error: {e}")

print("\n" + "=" * 50)
print("Setup test complete!")
print("=" * 50)