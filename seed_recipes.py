import os
import sys
import json
import django
from datetime import datetime
from bson import ObjectId

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartchef.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

try:
    from recipes import db
except ImportError:
    # If running from within 'recipes' folder
    import db

def seed_recipes():
    print("🚀 Starting recipe seeding process from recipes.json...")
    
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recipes.json')
    
    if not os.path.exists(json_path):
        print(f"❌ File not found: {json_path}")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            recipes_data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading recipes.json: {e}")
        return

    database = db.get_database()
    if database is None:
        print("❌ Database connection failed. Please ensure MongoDB Atlas is reachable.")
        return

    count = 0
    # User ID for seeded recipes (optional - set to None or a specific admin user ID)
    # If you have an admin user, you can find their ID here
    admin_user = database.users.find_one({"username": "admin"})
    admin_id = admin_user["_id"] if admin_user else None

    for item in recipes_data:
        # Check if already exists
        if database.recipes.find_one({"title": item["title"]}):
            # print(f"⏩ Recipe '{item['title']}' already exists, skipping...")
            continue
            
        # Multilingual support
        title_hi = item.get("title_hi", "")
        title_mr = item.get("title_mr", "")
        
        # Split instructions into steps if it's a string
        instr = item.get("instructions", "")
        if isinstance(instr, str):
            steps = [s.strip() for s in instr.split(".") if s.strip()]
        else:
            steps = instr

        # Steps in other languages
        instr_hi = item.get("instructions_hi", "")
        if isinstance(instr_hi, str) and instr_hi:
            steps_hi = [s.strip() for s in instr_hi.split(".") if s.strip()]
        else:
            steps_hi = item.get("steps_hi", [])

        instr_mr = item.get("instructions_mr", "")
        if isinstance(instr_mr, str) and instr_mr:
            steps_mr = [s.strip() for s in instr_mr.split(".") if s.strip()]
        else:
            steps_mr = item.get("steps_mr", [])
        
        recipe = {
            "title": item["title"],
            "title_hi": title_hi,
            "title_mr": title_mr,
            "category": item.get("category", "veg"),
            "ingredients": item.get("ingredients", ["Various high-quality ingredients"]),
            "steps": steps,
            "steps_hi": steps_hi,
            "steps_mr": steps_mr,
            "prep_time": item.get("prep_time", "15 mins"),
            "cook_time": item.get("cook_time", "25 mins"),
            "servings": item.get("servings", 4),
            "image": item["image"],
            "created_by": admin_id,
            "created_at": datetime.now(),
            "likes": [],
            "ratings": [],
            "views": 0,
            "source": item.get("source", "Standard Seed")
        }
        
        database.recipes.insert_one(recipe)
        count += 1
        print(f"✅ Added {count}: {item['title']}")

    print(f"\n✨ Seeding completed! Successfully added {count} professional recipes to MongoDB.")

if __name__ == "__main__":
    seed_recipes()
