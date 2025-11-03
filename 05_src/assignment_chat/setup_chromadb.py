"""
Setup ChromaDB with Pitchfork music reviews data.
This script should be run once to initialize the vector database.
"""

import sys
from pathlib import Path

# Add 05_src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import json
import os
from dotenv import load_dotenv
from utils.logger import get_logger

_logs = get_logger(__name__)

src_dir = Path(__file__).parent.parent
load_dotenv(src_dir / ".env")
load_dotenv(src_dir / ".secrets")

# ChromaDB settings
CHROMA_URL = "http://localhost:8000"
COLLECTION_NAME = "pitchfork_music_reviews"

def load_pitchfork_reviews(max_reviews=500):
    """
    Load Pitchfork review content from JSONL file.
    Limit to max_reviews to keep the database manageable.
    """
    doc_path = src_dir / "documents" / "pitchfork_content.jsonl"
    reviews = []
    
    _logs.info(f"Loading reviews from {doc_path}")
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= max_reviews:
                break
            try:
                review = json.loads(line.strip())
                reviews.append(review)
            except json.JSONDecodeError:
                continue
    
    _logs.info(f"Loaded {len(reviews)} reviews")
    return reviews

def load_additional_data():
    """Load artist, genre, and other metadata"""
    data = {}
    
    # Load artists
    artists_path = src_dir / "documents" / "pitchfork_artists.jsonl"
    data['artists'] = {}
    with open(artists_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                artist = json.loads(line.strip())
                data['artists'][artist['reviewid']] = artist['artist']
            except:
                continue
    
    # Load reviews (for scores and metadata)
    reviews_path = src_dir / "documents" / "pitchfork_reviews.jsonl"
    data['reviews'] = {}
    with open(reviews_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                review = json.loads(line.strip())
                data['reviews'][review['reviewid']] = {
                    'title': review.get('title', ''),
                    'score': review.get('score', 0),
                    'pub_year': review.get('pub_year', 0)
                }
            except:
                continue
    
    _logs.info(f"Loaded {len(data['artists'])} artists and {len(data['reviews'])} review metadata")
    return data

def setup_collection():
    """Create or reset the ChromaDB collection"""
    _logs.info(f"Connecting to ChromaDB at {CHROMA_URL}")
    
    chroma_client = chromadb.HttpClient(host=CHROMA_URL)
    
    # Delete existing collection if it exists
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
        _logs.info(f"Deleted existing collection: {COLLECTION_NAME}")
    except:
        pass
    
    # Create new collection with OpenAI embeddings
    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
    )
    
    _logs.info(f"Created collection: {COLLECTION_NAME}")
    return collection

def populate_collection(collection, reviews, additional_data):
    """Add reviews to the collection"""
    _logs.info("Adding reviews to collection...")
    
    documents = []
    metadatas = []
    ids = []
    
    for review in reviews:
        reviewid = review.get('reviewid')
        content = review.get('content', '')
        
        if not content or not reviewid:
            continue
        
        # Get additional metadata
        artist = additional_data['artists'].get(reviewid, 'Unknown Artist')
        review_meta = additional_data['reviews'].get(reviewid, {})
        
        documents.append(content)
        metadatas.append({
            'reviewid': str(reviewid),
            'artist': artist,
            'title': review_meta.get('title', ''),
            'score': float(review_meta.get('score', 0)),
            'year': int(review_meta.get('pub_year', 0))
        })
        ids.append(f"review_{reviewid}")
    
    # Add to collection in batches
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        end_idx = min(i + batch_size, len(documents))
        collection.add(
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx],
            ids=ids[i:end_idx]
        )
        _logs.info(f"Added batch {i//batch_size + 1}: {end_idx}/{len(documents)} reviews")
    
    _logs.info(f"✅ Successfully added {len(documents)} reviews to collection")

def test_query(collection):
    """Test the collection with a sample query"""
    _logs.info("Testing collection with sample query...")
    
    results = collection.query(
        query_texts=["indie rock with great vocals"],
        n_results=3
    )
    
    _logs.info("Sample query results:")
    for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        _logs.info(f"\n{i+1}. {meta['artist']} - {meta['title']}")
        _logs.info(f"   Score: {meta['score']}")
        _logs.info(f"   Excerpt: {doc[:150]}...")

def main():
    """Main setup process"""
    try:
        # Load data
        reviews = load_pitchfork_reviews(max_reviews=500)
        additional_data = load_additional_data()
        
        # Setup ChromaDB
        collection = setup_collection()
        
        # Populate collection
        populate_collection(collection, reviews, additional_data)
        
        # Test query
        test_query(collection)
        
        _logs.info("\n✅ ChromaDB setup complete!")
        _logs.info(f"Collection '{COLLECTION_NAME}' is ready to use")
        
    except Exception as e:
        _logs.error(f"❌ Setup failed: {e}")
        raise

if __name__ == "__main__":
    main()
