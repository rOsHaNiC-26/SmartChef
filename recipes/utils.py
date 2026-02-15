import requests
from datetime import datetime
from . import db

def fetch_mealdb_recipes(limit=10):
    """
    Fetch recipes from TheMealDB (Free API) and save to MongoDB.
    
    This matches the user's request for 'Option 1: Recipe API Use Karna'.
    We use TheMealDB because it requires no API key for basic search.
    """
    # Categories to search to get a mix
    search_terms = ['Chicken', 'Paneer', 'Pasta', 'Curry', 'Cake']
    count = 0
    added_recipes = []
    
    for term in search_terms:
        if count >= limit:
            break
            
        try:
            url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={term}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            meals = data.get('meals')
            if not meals:
                continue
                
            database = db.get_database()
            if not database:
                print("[WARN] Database not connected. Cannot save API recipes.")
                return 0
                
            for meal in meals:
                if count >= limit:
                    break
                
                # Check for duplicate
                existing = database.recipes.find_one({'title': meal['strMeal']})
                if existing:
                    continue
                
                # Convert ingredients from their format (strIngredient1, strIngredient2...)
                ingredients = []
                for i in range(1, 21):
                    ing = meal.get(f'strIngredient{i}')
                    measure = meal.get(f'strMeasure{i}')
                    if ing and ing.strip():
                        ingredients.append(f"{ing.strip()} - {measure.strip() if measure else ''}")
                
                # Convert instructions to list
                instructions_text = meal.get('strInstructions', '')
                steps = [s.strip() for s in instructions_text.replace('\r', '').split('\n') if s.strip()]
                
                # Determine category
                cat_map = {'Vegetarian': 'veg', 'Chicken': 'non-veg', 'Beef': 'non-veg', 'Dessert': 'dessert'}
                api_cat = meal.get('strCategory', 'Vegetarian')
                category = cat_map.get(api_cat, 'veg' if 'Paneer' in meal['strMeal'] else 'non-veg')
                
                new_recipe = {
                    'title': meal['strMeal'],
                    'category': category,
                    'ingredients': ingredients,
                    'steps': steps,
                    'prep_time': '15 mins', # Default as API doesn't provide
                    'cook_time': '30 mins', # Default
                    'servings': 4,
                    'image': meal['strMealThumb'],
                    'created_by': None, # System/API user
                    'created_at': datetime.now(),
                    'likes': [],
                    'ratings': [],
                    'views': 0,
                    'source': 'TheMealDB' 
                }
                
                database.recipes.insert_one(new_recipe)
                added_recipes.append(new_recipe['title'])
                count += 1
                
        except Exception as e:
            print(f"[ERROR] Failed to fetch for {term}: {e}")
            
    return count
