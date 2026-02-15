
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Load environment variables
load_dotenv(os.path.join(BASE_DIR, '.env'))

# MongoDB Connection
uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
name = os.getenv('MONGODB_NAME', 'smartchef')

print(f"Testing connection to: {uri}")

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    db = client[name]
    client.admin.command('ping')
    print(f"✅ Connected to MongoDB ({name}) successfully!")
    
    # Check collections
    collections = db.list_collection_names()
    print(f"Collections: {collections}")
    
    # Count recipes
    count = db.recipes.count_documents({})
    print(f"Total recipes: {count}")
    
except Exception as e:
    import traceback
    print(f"❌ MongoDB connection failed: {e}")
    traceback.print_exc()
