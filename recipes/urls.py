"""
URL patterns for SmartChef recipes app
"""

from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.splash, name='splash'),
    path('home/', views.home, name='home'),
    path('recipes/', views.recipes_list, name='recipes'),
    path('recipe/<str:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    
    # My Recipes
    path('my-recipes/', views.my_recipes, name='my_recipes'),
    path('add-recipe/', views.add_recipe, name='add_recipe'),
    path('edit-recipe/<str:recipe_id>/', views.edit_recipe, name='edit_recipe'),
    path('delete-recipe/<str:recipe_id>/', views.delete_recipe, name='delete_recipe'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile & Settings
    path('profile/', views.profile_view, name='profile'),
    path('settings/update/', views.update_settings, name='update_settings'),
    path('support/', views.customer_support, name='support'),
    path('rate-us/', views.rate_us, name='rate_us'),
    
    # Interactions
    path('like/<str:recipe_id>/', views.toggle_like, name='toggle_like'),
    path('rate/<str:recipe_id>/', views.add_rating, name='add_rating'),
    path('comment/<str:recipe_id>/', views.add_comment, name='add_comment'),
    
    
    # Tools
    path('tools/load-recipes/', views.load_api_recipes, name='load_api_recipes'),

    # API
    path('api/recipes/', views.api_recipes, name='api_recipes'),
]
