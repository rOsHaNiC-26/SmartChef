"""
Views for SmartChef Recipe Application
"""

import os
import uuid
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from . import db
from .utils import fetch_mealdb_recipes


def process_recipe_data(recipe):
    """Helper to add calculated fields like avg_rating and localized category"""
    # Ratings
    ratings = recipe.get('ratings', [])
    recipe['avg_rating'] = round(sum(ratings) / len(ratings), 1) if ratings else 4.5
    recipe['rating_count'] = len(ratings)
    
    # Likes count
    likes = recipe.get('likes', [])
    recipe['likes_count'] = len(likes) if isinstance(likes, list) else likes
    
    # Human-readable category
    cat_map = {'veg': 'Vegetarian', 'non-veg': 'Non-Vegetarian', 'dessert': 'Desserts', 'desserts': 'Desserts', 'drinks': 'Drinks', 'snacks': 'Snacks'}
    recipe['category_name'] = cat_map.get(recipe.get('category'), 'Other')
    return recipe


def add_notification(request, message, type='success'):
    """Add notification to session"""
    if 'notifications' not in request.session:
        request.session['notifications'] = []
    request.session['notifications'].append({
        'message': message,
        'type': type  # success, error, warning, info
    })
    request.session.modified = True


def login_required(view_func):
    """Decorator to require login"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            add_notification(request, 'Please login to continue', 'warning')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ==================== HOME & PAGES ====================

def splash(request):
    """Startup Splash Screen with Animation"""
    return render(request, 'splash.html')

def home(request):
    """Home page with trending recipes"""
    recipes = db.get_all_recipes(limit=6)
    categories = db.get_categories()
    
    # Calculate trending (top 3 by likes)
    all_recipes = db.get_all_recipes(limit=100) # Get a pool
    # Handle both new array-style likes and old numeric likes
    def get_likes_count(r):
        likes = r.get('likes', 0)
        return len(likes) if isinstance(likes, list) else likes
        
    trending = sorted(all_recipes, key=get_likes_count, reverse=True)[:3]
    
    # Process data
    recipes = [process_recipe_data(r) for r in recipes]
    trending = [process_recipe_data(r) for r in trending]
    
    return render(request, 'home.html', {
        'recipes': recipes,
        'trending': trending,
        'categories': categories,
        'page_title': 'SmartChef - Cook, Share, Inspire'
    })


def recipes_list(request):
    """All recipes page with filters"""
    category = request.GET.get('category', 'all')
    search = request.GET.get('search', '')
    
    recipes = db.get_all_recipes(category=category, search=search)
    # Process recipes
    recipes = [process_recipe_data(r) for r in recipes]
    categories = db.get_categories()
    
    return render(request, 'recipes.html', {
        'recipes': recipes,
        'categories': categories,
        'current_category': category,
        'search_query': search,
        'page_title': 'All Recipes'
    })


def recipe_detail(request, recipe_id):
    """Single recipe detail page with comments and ratings"""
    recipe = db.get_recipe_by_id(recipe_id)
    
    if not recipe:
        add_notification(request, 'Recipe not found', 'error')
        return redirect('recipes')
    
    # Increment view count
    db.increment_recipe_views(recipe_id)
    
    # Process data
    recipe = process_recipe_data(recipe)
    
    # Get comments
    comments = db.get_comments(recipe_id)
    
    # Check if user liked it
    user_id = request.session.get('user_id')
    user_liked = False
    if user_id:
        likes = recipe.get('likes', [])
        if isinstance(likes, list):
            try:
                from bson.objectid import ObjectId
                user_liked = ObjectId(user_id) in likes
            except:
                user_liked = user_id in likes

    # Prepare steps for translation
    steps_en = recipe.get('steps', [])
    steps_hi = recipe.get('steps_hi', [])
    steps_mr = recipe.get('steps_mr', [])
    
    # Ensure consistency
    while len(steps_hi) < len(steps_en): steps_hi.append(steps_en[len(steps_hi)])
    while len(steps_mr) < len(steps_en): steps_mr.append(steps_en[len(steps_mr)])
    
    translated_steps = []
    for i in range(len(steps_en)):
        translated_steps.append({
            'en': steps_en[i],
            'hi': steps_hi[i],
            'mr': steps_mr[i]
        })
    
    return render(request, 'recipe_detail.html', {
        'recipe': recipe,
        'translated_steps': translated_steps,
        'comments': comments,
        'avg_rating': recipe['avg_rating'],
        'rating_count': recipe['rating_count'],
        'user_liked': user_liked,
        'page_title': recipe.get('title', 'Recipe')
    })


# ==================== MY RECIPES ====================

@login_required
def my_recipes(request):
    """View to manage ALL recipes (renamed from 'my_recipes' contextually)"""
    # By passing user_id=None, we get all recipes from db.py
    recipes = db.get_user_recipes(None)
    
    return render(request, 'my_recipes.html', {
        'recipes': recipes,
        'page_title': 'Manage All Recipes'
    })


@login_required
def add_recipe(request):
    """Add new recipe form"""
    categories = db.get_categories()[1:]  # Exclude 'All'
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', 'veg')
        ingredients = request.POST.get('ingredients', '').strip().split('\n')
        steps = request.POST.get('steps', '').strip().split('\n')
        prep_time = request.POST.get('prep_time', '0 mins')
        cook_time = request.POST.get('cook_time', '0 mins')
        servings = int(request.POST.get('servings', 2))
        
        # Handle image upload
        image_url = '/static/images/default-recipe.jpg'
        if 'image' in request.FILES:
            image = request.FILES['image']
            filename = f"{uuid.uuid4().hex}_{image.name}"
            filepath = os.path.join(settings.MEDIA_ROOT, 'recipes', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            image_url = f'/media/recipes/{filename}'
        
        # Clean ingredients and steps
        ingredients = [i.strip() for i in ingredients if i.strip()]
        steps = [s.strip() for s in steps if s.strip()]
        
        user_id = request.session.get('user_id')
        recipe, error = db.create_recipe(
            user_id, title, category, ingredients, steps,
            prep_time, cook_time, servings, image_url
        )
        
        if error:
            add_notification(request, error, 'error')
        else:
            add_notification(request, 'Recipe added successfully!', 'success')
            return redirect('my_recipes')
    
    return render(request, 'add_recipe.html', {
        'categories': categories,
        'page_title': 'Add New Recipe'
    })


@login_required
def edit_recipe(request, recipe_id):
    """Edit existing recipe"""
    user_id = request.session.get('user_id')
    recipe = db.get_recipe_by_id(recipe_id)
    
    if not recipe:
        add_notification(request, 'Recipe not found', 'error')
        return redirect('my_recipes')
    
    # Ownership check removed for global management
    # if str(recipe.get('created_by')) != user_id:
    #     add_notification(request, 'You can only edit your own recipes', 'error')
    #     return redirect('my_recipes')
    
    categories = db.get_categories()[1:]
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', 'veg')
        ingredients = request.POST.get('ingredients', '').strip().split('\n')
        steps = request.POST.get('steps', '').strip().split('\n')
        prep_time = request.POST.get('prep_time', '0 mins')
        cook_time = request.POST.get('cook_time', '0 mins')
        servings = int(request.POST.get('servings', 2))
        
        ingredients = [i.strip() for i in ingredients if i.strip()]
        steps = [s.strip() for s in steps if s.strip()]
        
        success = db.update_recipe(
            recipe_id, user_id,
            title=title, category=category, ingredients=ingredients,
            steps=steps, prep_time=prep_time, cook_time=cook_time, servings=servings
        )
        
        if success:
            add_notification(request, 'Recipe updated successfully!', 'success')
            return redirect('my_recipes')
        else:
            add_notification(request, 'Failed to update recipe', 'error')
    
    return render(request, 'edit_recipe.html', {
        'recipe': recipe,
        'categories': categories,
        'page_title': f'Edit - {recipe.get("title")}'
    })


@login_required
def delete_recipe(request, recipe_id):
    """Delete a recipe"""
    user_id = request.session.get('user_id')
    
    if request.method == 'POST':
        success = db.delete_recipe(recipe_id, user_id)
        if success:
            add_notification(request, 'Recipe deleted', 'success')
        else:
            add_notification(request, 'Failed to delete recipe', 'error')
    
    return redirect('my_recipes')


# ==================== AUTHENTICATION ====================

def login_view(request):
    """User login"""
    user_id = request.session.get('user_id')
    if user_id:
        if db.get_user_by_id(user_id):
            return redirect('home')
        else:
            request.session.flush()
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user, error = db.authenticate_user(username, password)
        
        if error:
            add_notification(request, error, 'error')
        else:
            request.session['user_id'] = str(user['_id'])
            request.session['username'] = user['username']
            add_notification(request, f'Welcome back, {user["username"]}!', 'success')
            
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    
    return render(request, 'login.html', {
        'page_title': 'Login'
    })


def register_view(request):
    """User registration"""
    user_id = request.session.get('user_id')
    if user_id:
        if db.get_user_by_id(user_id):
            return redirect('home')
        else:
            request.session.flush()
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        if len(username) < 3:
            add_notification(request, 'Username must be at least 3 characters', 'error')
        elif len(password) < 6:
            add_notification(request, 'Password must be at least 6 characters', 'error')
        elif password != confirm_password:
            add_notification(request, 'Passwords do not match', 'error')
        else:
            user, error = db.create_user(username, email, password)
            
            if error:
                add_notification(request, error, 'error')
            else:
                request.session['user_id'] = str(user['_id'])
                request.session['username'] = user['username']
                add_notification(request, 'Account created successfully!', 'success')
                return redirect('home')
    
    return render(request, 'register.html', {
        'page_title': 'Create Account'
    })


def logout_view(request):
    """User logout"""
    username = request.session.get('username', 'User')
    request.session.flush()
    add_notification(request, f'Goodbye, {username}! See you soon', 'info')
    return redirect('home')


# ==================== PROFILE & SETTINGS ====================

@login_required
def profile_view(request):
    """User profile page"""
    user_id = request.session.get('user_id')
    user = db.get_user_by_id(user_id)
    
    if not user:
        return redirect('logout')
    
    # Get user stats
    user_recipes = db.get_user_recipes(user_id)
    total_recipes = len(user_recipes)
    total_views = sum(r.get('views', 0) for r in user_recipes)
    total_likes = sum(len(r.get('likes', [])) if isinstance(r.get('likes', []), list) else r.get('likes', 0) for r in user_recipes)
    
    return render(request, 'profile.html', {
        'user': user,
        'total_recipes': total_recipes,
        'total_views': total_views,
        'total_likes': total_likes,
        'page_title': 'My Profile'
    })


@login_required
def update_settings(request):
    """Update user settings via AJAX"""
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        language = request.POST.get('language')
        theme = request.POST.get('theme')
        
        success = db.update_user_settings(user_id, language=language, theme=theme)
        
        if success:
            msg = 'Settings updated!'
            if language:
                lang_names = {'en': 'English', 'hi': 'हिंदी', 'mr': 'मराठी'}
                msg = f'Language changed to {lang_names.get(language, language)}'
            elif theme:
                msg = f'{theme.title()} mode activated'
            
            add_notification(request, msg, 'success')
            return JsonResponse({'success': True, 'message': msg})
        
        return JsonResponse({'success': False, 'message': 'Failed to update settings'})
    
    return redirect('profile')


def customer_support(request):
    """Customer Support Page"""
    return render(request, 'support.html', {'page_title': 'Customer Support'})

def rate_us(request):
    """Rate Us Page"""
    return render(request, 'rate_us.html', {'page_title': 'Rate SmartChef'})


# ==================== INTERACTION VIEWS ====================

@login_required
@require_http_methods(["POST"])
def toggle_like(request, recipe_id):
    """AJAX like/unlike toggle"""
    user_id = request.session.get('user_id')
    success, action = db.toggle_like_recipe(recipe_id, user_id)
    
    if success:
        # Get new count
        recipe = db.get_recipe_by_id(recipe_id)
        likes = recipe.get('likes', [])
        count = len(likes) if isinstance(likes, list) else 0
        return JsonResponse({'success': True, 'action': action, 'count': count})
        
    return JsonResponse({'success': False, 'message': 'Failed to like recipe'}, status=400)


@login_required
@require_http_methods(["POST"])
def add_rating(request, recipe_id):
    """Submit a rating"""
    user_id = request.session.get('user_id')
    value = request.POST.get('rating')
    
    if not value or not value.isdigit():
        return JsonResponse({'success': False, 'message': 'Invalid rating'}, status=400)
        
    success = db.add_rating(recipe_id, user_id, int(value))
    if success:
        add_notification(request, 'Thanks for rating!', 'success')
        return JsonResponse({'success': True})
        
    return JsonResponse({'success': False, 'message': 'Failed to submit rating'}, status=400)


@login_required
@require_http_methods(["POST"])
def add_comment(request, recipe_id):
    """Post a comment"""
    user_id = request.session.get('user_id')
    text = request.POST.get('text', '').strip()
    
    if not text:
        add_notification(request, 'Comment cannot be empty', 'error')
        return redirect('recipe_detail', recipe_id=recipe_id)
        
    comment = db.add_comment(recipe_id, user_id, text)
    if comment:
        add_notification(request, 'Comment posted!', 'success')
    else:
        add_notification(request, 'Failed to post comment', 'error')
        
    return redirect('recipe_detail', recipe_id=recipe_id)


# ==================== API ENDPOINTS ====================

def api_recipes(request):
    """API endpoint for recipes"""
    category = request.GET.get('category', 'all')
    search = request.GET.get('search', '')
    
    recipes = db.get_all_recipes(category=category, search=search)
    
    # Convert ObjectId to string for JSON and process data
    processed = []
    for recipe in recipes:
        recipe = process_recipe_data(recipe)
        recipe['_id'] = str(recipe.get('_id', ''))
        if 'created_by' in recipe:
            recipe['created_by'] = str(recipe['created_by'])
        if 'created_at' in recipe:
            recipe['created_at'] = str(recipe['created_at'])
        processed.append(recipe)
    
    return JsonResponse({'recipes': processed})
# ==================== SETTINGS & TOOLS ====================

@login_required
def load_api_recipes(request):
    """Fetch recipes from external API (TheMealDB)"""
    count = fetch_mealdb_recipes(limit=10)
    if count > 0:
        add_notification(request, f'Successfully imported {count} new recipes from the internet!', 'success')
    else:
        add_notification(request, 'No new recipes found or database offline.', 'warning')
        
    return redirect('recipes')
