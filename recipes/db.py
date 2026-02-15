"""
MongoDB Database Connection and Operations for SmartChef
"""

import os
import certifi
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt
from django.conf import settings

# MongoDB Connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_NAME = os.getenv('MONGODB_NAME', 'smartchef')

client = None
db = None


def get_database():
    """Get MongoDB database connection"""
    global client, db
    
    # Get connection details from Django settings
    uri = getattr(settings, 'MONGODB_URI', 'mongodb://localhost:27017/')
    name = getattr(settings, 'MONGODB_NAME', 'smartchef')
    
    if db is None:
        try:
            # Use certifi for SSL certificates on Windows
            # Set a 2.5 second timeout so the app doesn't hang if DB is offline
            # standard connection attempt
            client = MongoClient(
                uri, 
                serverSelectionTimeoutMS=2500,
                tlsCAFile=certifi.where() if 'mongodb+srv' in uri else None
            )
            # Test connection immediately
            client.admin.command('ping')
            db = client[name]
            print(f"[OK] Connected to MongoDB ({name}) successfully!")
        except Exception as e:
            print(f"[WARN] First connection attempt failed: {e}")
            try:
                # Retry with less strict SSL (common fix for school/work networks)
                print("[INFO] Retrying with tlsAllowInvalidCertificates...")
                client = MongoClient(
                    uri,
                    serverSelectionTimeoutMS=2500,
                    tlsAllowInvalidCertificates=True
                )
                client.admin.command('ping')
                db = client[name]
                print(f"[OK] Connected to MongoDB ({name}) with SSL bypass!")
            except Exception as e2:
                print(f"[ERROR] MongoDB connection critical failure: {e2}")
                print("[INFO] Using local fallback mode...")
                db = None
                return None
    return db


def close_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()


# ==================== USER OPERATIONS ====================

def create_user(username, email, password):
    """Create a new user"""
    try:
        # Check connection first
        db_obj = get_database()
        if db_obj is None:
            return None, "Database connection timeout. Please check your internet."
        db = db_obj
        
        # Check if user already exists
        existing = db.users.find_one({'$or': [{'username': username}, {'email': email}]})
        if existing:
            if existing.get('username') == username:
                return None, "Username already exists"
            return None, "Email already exists"
        
        # Hash password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user = {
            'username': username,
            'email': email,
            'password': hashed,
            'language': 'en',  # Default English
            'theme': 'light',  # Default light mode
            'created_at': datetime.now(),
            'favorites': []
        }
        
        result = db.users.insert_one(user)
        user['_id'] = result.inserted_id
        return user, None
    except Exception as e:
        print(f"[ERROR] Registration error: {e}")
        return None, "Database error during registration"


def authenticate_user(username, password):
    """Authenticate user login"""
    try:
        db_obj = get_database()
        if db_obj is None:
            return None, "Database connection timeout. Please check your internet."
        db = db_obj
        
        user = db.users.find_one({'$or': [{'username': username}, {'email': username}]})
        if not user:
            return None, "User not found"
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return user, None
        return None, "Invalid password"
    except Exception as e:
        print(f"[ERROR] Auth error: {e}")
        return None, "Database error occurred"


def get_user_by_id(user_id):
    """Get user by ID"""
    db = get_database()
    if db is None:
        return None
    
    try:
        return db.users.find_one({'_id': ObjectId(user_id)})
    except:
        return None


def update_user_settings(user_id, language=None, theme=None):
    """Update user settings"""
    db = get_database()
    if db is None:
        return False
    
    update = {}
    if language:
        update['language'] = language
    if theme:
        update['theme'] = theme
    
    if update:
        db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update})
        return True
    return False


# ==================== RECIPE OPERATIONS ====================

def get_all_recipes(category=None, search=None, limit=50):
    """Get all recipes with optional filters"""
    try:
        db = get_database()
        if db is None:
            return get_sample_recipes()
        
        query = {}
        
        if category and category != 'all':
            query['category'] = category
        
        if search:
            query['$or'] = [
                {'title': {'$regex': search, '$options': 'i'}},
                {'ingredients': {'$regex': search, '$options': 'i'}},
                {'steps': {'$regex': search, '$options': 'i'}},
                {'category': {'$regex': search, '$options': 'i'}}
            ]
        
        recipes = list(db.recipes.find(query).sort('created_at', -1).limit(limit))
        
        # Get user info and add 'id' for each recipe
        for recipe in recipes:
            recipe['id'] = str(recipe['_id'])
            user = db.users.find_one({'_id': recipe.get('created_by')})
            recipe['author'] = user.get('username', 'Unknown') if user else 'Unknown'
        
        return recipes if recipes else get_sample_recipes()
    except Exception as e:
        print(f"[WARN] Error fetching recipes: {e}")
        return get_sample_recipes()


def get_recipe_by_id(recipe_id):
    """Get single recipe by ID with sample data fallback"""
    try:
        # Check if it's a sample ID
        if isinstance(recipe_id, str) and recipe_id.startswith('sample'):
            for r in get_sample_recipes():
                if r['id'] == recipe_id:
                    return r

        db = get_database()
        if db is None:
            # Last resort: check samples if DB is offline
            for r in get_sample_recipes():
                if r['id'] == recipe_id:
                    return r
            return None
        
        recipe = db.recipes.find_one({'_id': ObjectId(recipe_id)})
        if recipe:
            recipe['id'] = str(recipe['_id'])
            user = db.users.find_one({'_id': recipe.get('created_by')})
            recipe['author'] = user.get('username', 'Unknown') if user else 'Unknown'
        return recipe
    except Exception as e:
        print(f"[ERROR] Error fetching recipe: {e}")
        # One more check for sample data on error (like invalid ObjectId)
        for r in get_sample_recipes():
            if r['id'] == recipe_id:
                return r
        return None


def get_user_recipes(user_id=None):
    """Get recipes. If user_id is provided, gets user's recipes. Otherwise gets ALL."""
    db = get_database()
    if db is None:
        return []
    
    try:
        query = {'created_by': ObjectId(user_id)} if user_id else {}
        recipes = list(db.recipes.find(query).sort('created_at', -1))
        
        # Resolve user names
        for r in recipes:
            r['id'] = str(r['_id'])
            if r.get('created_by'):
                creator = db.users.find_one({'_id': r['created_by']})
                r['author'] = creator['username'] if creator else "Admin"
            else:
                r['author'] = r.get('source', "Chef")
        return recipes
    except Exception as e:
        print(f"[ERROR] get_user_recipes error: {e}")
        return []


def create_recipe(user_id, title, category, ingredients, steps, prep_time, cook_time, servings, image_url=None, **kwargs):
    """Create a new recipe with optional multilingual fields"""
    try:
        db = get_database()
        if db is None:
            return None, "Database connection failed"
        
        recipe = {
            'title': title,
            'title_hi': kwargs.get('title_hi', ''),
            'title_mr': kwargs.get('title_mr', ''),
            'category': category,
            'ingredients': ingredients,
            'steps': steps,
            'steps_hi': kwargs.get('steps_hi', []),
            'steps_mr': kwargs.get('steps_mr', []),
            'prep_time': prep_time,
            'cook_time': cook_time,
            'servings': servings,
            'image': image_url or '/static/images/default-recipe.jpg',
            'created_by': ObjectId(user_id) if user_id else None,
            'created_at': datetime.now(),
            'likes': [],  # Store user IDs who liked
            'ratings': [],  # Store rating values
            'views': 0
        }
        
        result = db.recipes.insert_one(recipe)
        recipe['_id'] = result.inserted_id
        return recipe, None
    except Exception as e:
        print(f"[ERROR] Error creating recipe: {e}")
        return None, "Database error"


def update_recipe(recipe_id, user_id, **kwargs):
    """Update existing recipe including potential translations"""
    db = get_database()
    if db is None:
        return False
    
    try:
        # Check if recipe exists
        recipe = db.recipes.find_one({'_id': ObjectId(recipe_id)})
        if not recipe:
            return False
            
        # Extract multilingual fields if they exist in kwargs
        update = {k: v for k, v in kwargs.items() if v is not None}
        if update:
            db.recipes.update_one({'_id': ObjectId(recipe_id)}, {'$set': update})
        return True
    except:
        return False


def delete_recipe(recipe_id, user_id):
    """Delete a recipe. (Ownership check relaxed for project management mode)"""
    db = get_database()
    if db is None:
        return False
    
    try:
        result = db.recipes.delete_one({'_id': ObjectId(recipe_id)})
        return result.deleted_count > 0
    except:
        return False


def increment_recipe_views(recipe_id):
    """Increment recipe view count"""
    db = get_database()
    if db is None:
        return
    
    try:
        db.recipes.update_one({'_id': ObjectId(recipe_id)}, {'$inc': {'views': 1}})
    except:
        pass


def toggle_like_recipe(recipe_id, user_id):
    """Toggle like status for a recipe"""
    # Demo mode for sample recipes
    if isinstance(recipe_id, str) and recipe_id.startswith('sample'):
        return True, "liked"

    db = get_database()
    if db is None:
        return False, "Database connection error"
    
    try:
        recipe = db.recipes.find_one({'_id': ObjectId(recipe_id)})
        if not recipe:
            return False, "Recipe not found"
        
        # In case 'likes' is still a number (migration)
        likes = recipe.get('likes', [])
        if not isinstance(likes, list):
            likes = []
            
        uid = ObjectId(user_id)
        if uid in likes:
            # Unlike
            db.recipes.update_one({'_id': ObjectId(recipe_id)}, {'$pull': {'likes': uid}})
            return True, "unliked"
        else:
            # Like
            db.recipes.update_one({'_id': ObjectId(recipe_id)}, {'$push': {'likes': uid}})
            return True, "liked"
    except Exception as e:
        print(f"[ERROR] Like toggle error: {e}")
        return False, str(e)


def add_rating(recipe_id, user_id, rating_value):
    """Add or update user's rating for a recipe"""
    if isinstance(recipe_id, str) and recipe_id.startswith('sample'):
        return True

    db = get_database()
    if db is None:
        return False
    
    try:
        # We store simple list of ratings in recipe document for now
        # For professional system, we'd store {user_id, value} pairs
        # But let's stick to the user's requested logic
        db.recipes.update_one(
            {'_id': ObjectId(recipe_id)},
            {'$push': {'ratings': int(rating_value)}}
        )
        return True
    except:
        return False


def get_comments(recipe_id):
    """Get comments for a recipe"""
    db = get_database()
    if db is None:
        return []
        
    try:
        comments = list(db.comments.find({'recipe_id': ObjectId(recipe_id)}).sort('created_at', -1))
        for comment in comments:
            comment['id'] = str(comment['_id'])
            user = db.users.find_one({'_id': comment.get('user_id')})
            comment['author'] = user.get('username', 'Unknown') if user else 'Unknown'
            # Format date manually if needed or just return datetime
        return comments
    except:
        return []


def add_comment(recipe_id, user_id, text):
    """Add a new comment"""
    if isinstance(recipe_id, str) and recipe_id.startswith('sample'):
        return {'id': 'sample_comm', 'text': text, 'author': 'You', 'created_at': datetime.now()}

    db = get_database()
    if db is None:
        return None
        
    try:
        comment = {
            'recipe_id': ObjectId(recipe_id),
            'user_id': ObjectId(user_id),
            'text': text,
            'created_at': datetime.now()
        }
        result = db.comments.insert_one(comment)
        comment['_id'] = result.inserted_id
        return comment
    except:
        return None


# ==================== SAMPLE DATA ====================

def get_sample_recipes():
    """Return sample recipes when database is not available"""
    return [
        {
            '_id': 'sample1',
            'id': 'sample1',
            'title': 'Paneer Butter Masala',
            'category': 'veg',
            'ingredients': ['Paneer - 250g', 'Butter - 50g', 'Tomato - 4', 'Cream - 100ml', 'Garam Masala - 1 tsp'],
            'steps': [
                'Cut paneer into cubes and lightly fry',
                'Blend tomatoes to make puree',
                'Heat butter and add tomato puree',
                'Add spices and cook for 5 minutes',
                'Add cream and paneer, simmer for 10 minutes'
            ],
            'prep_time': '15 mins',
            'cook_time': '30 mins',
            'servings': 4,
            'image': '/static/images/paneer-butter-masala.jpg',
            'author': 'Chef Ravi',
            'author': 'Chef Ravi',
            'likes': ['sample_user1', 'sample_user2'],
            'views': 1520,
            'ratings': [5, 4, 5, 5],
            'created_at': datetime.now()
        },
        {
            '_id': 'sample2',
            'id': 'sample2',
            'title': 'Chicken Biryani',
            'category': 'non-veg',
            'ingredients': ['Chicken - 500g', 'Basmati Rice - 2 cups', 'Onion - 3', 'Yogurt - 1 cup', 'Biryani Masala - 2 tbsp'],
            'steps': [
                'Marinate chicken with yogurt and spices',
                'Fry onions until golden brown',
                'Cook marinated chicken partially',
                'Layer rice and chicken alternately',
                'Dum cook for 30 minutes'
            ],
            'prep_time': '30 mins',
            'cook_time': '45 mins',
            'servings': 6,
            'image': '/static/images/chicken-biryani.jpg',
            'author': 'Chef Ahmad',
            'author': 'Chef Ahmad',
            'likes': ['sample_user3', 'sample_user4', 'sample_user5'],
            'views': 3200,
            'ratings': [5, 5, 5, 4, 5],
            'created_at': datetime.now()
        },
        {
            '_id': 'sample3',
            'id': 'sample3',
            'title': 'Mango Lassi',
            'category': 'drinks',
            'ingredients': ['Mango - 2', 'Yogurt - 2 cups', 'Sugar - 4 tbsp', 'Ice cubes', 'Cardamom powder'],
            'steps': [
                'Peel and chop mangoes',
                'Blend mango with yogurt',
                'Add sugar and cardamom',
                'Blend until smooth',
                'Serve cold with ice'
            ],
            'prep_time': '5 mins',
            'cook_time': '0 mins',
            'servings': 2,
            'image': '/static/images/mango-lassi.jpg',
            'author': 'Chef Priya',
            'author': 'Chef Priya',
            'likes': ['sample_user6'],
            'views': 980,
            'ratings': [4, 4, 3, 5],
            'created_at': datetime.now()
        },
        {
            '_id': 'sample4',
            'id': 'sample4',
            'title': 'Gulab Jamun',
            'category': 'desserts',
            'ingredients': ['Khoya - 200g', 'Maida - 2 tbsp', 'Sugar - 2 cups', 'Cardamom', 'Rose water'],
            'steps': [
                'Make dough with khoya and maida',
                'Shape into small balls',
                'Deep fry on low heat until golden',
                'Make sugar syrup with cardamom',
                'Soak jamuns in warm syrup'
            ],
            'prep_time': '20 mins',
            'cook_time': '30 mins',
            'servings': 12,
            'image': '/static/images/gulab-jamun.jpg',
            'author': 'Chef Sunita',
            'likes': ['sample_user7', 'sample_user8'],
            'views': 2100,
            'ratings': [5, 5, 4, 3],
            'created_at': datetime.now()
        }
    ]


def get_categories():
    """Get available recipe categories"""
    return [
        {'id': 'all', 'name': 'All Recipes', 'name_hi': 'सभी रेसिपी', 'name_mr': 'सर्व रेसिपी', 'icon': '🍽️'},
        {'id': 'veg', 'name': 'Vegetarian', 'name_hi': 'शाकाहारी', 'name_mr': 'शाकाहारी', 'icon': '🥗'},
        {'id': 'non-veg', 'name': 'Non-Vegetarian', 'name_hi': 'मांसाहारी', 'name_mr': 'मांसाहारी', 'icon': '🍗'},
        {'id': 'desserts', 'name': 'Desserts', 'name_hi': 'मिठाई', 'name_mr': 'मिठाई', 'icon': '🍰'},
        {'id': 'drinks', 'name': 'Drinks', 'name_hi': 'पेय', 'name_mr': 'पेय', 'icon': '🥤'},
        {'id': 'snacks', 'name': 'Snacks', 'name_hi': 'नाश्ता', 'name_mr': 'स्नॅक्स', 'icon': '🍿'},
    ]
