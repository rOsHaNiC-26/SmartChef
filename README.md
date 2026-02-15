# 👨‍🍳 SmartChef - Recipe Sharing Web Application

A beautiful, full-featured recipe sharing web application built with **Django** and **MongoDB**. Users can share their recipes, discover new dishes, and connect with food lovers.

![SmartChef](static/images/paneer-butter-masala.jpg)

## ✨ Features

### 🏁 Startup Experience
- **Splash Screen** - Modern Neon Constellation animation (Particles.js) before app loads
- **Logo Animation** - Sleek brand entry animation

### 🏠 Core Features
- **Home Page** - Beautiful introduction with featured recipes
- **Recipes Page** - Browse all recipes with category filters & search
- **My Recipes** - Manage your personal recipe collection
- **Recipe Detail** - Full recipe with ingredients, steps, and sharing options
- **Customer Support** - Dedicated support page for user inquiries
- **Rate Us** - Interactive 5-star rating system

### 🔐 Authentication
- User Registration & Login
- Secure password hashing (bcrypt)
- Session-based authentication
- Profile management

### 👤 User Profile
- **Language Settings** - English, Hindi (हिंदी), Marathi (मराठी)
- **Theme Settings** - Light ☀️ / Dark 🌙 mode
- User statistics (recipes, views, likes)

### 🔔 Notifications
- **Notification Bell** - Navbar icon for managing alerts
- **Toast Notifications** - Real-time feedback for all operations

### 📱 Responsive Design
- Works on all devices
- Mobile-friendly navigation
- Print-ready recipe pages

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Django Templates, HTML5, CSS3, JavaScript |
| **Backend** | Django (Python) |
| **Database** | MongoDB Atlas |
| **Connector** | PyMongo |
| **Auth** | bcrypt for password hashing |

## 📁 Project Structure

```
SmartChef/
├── smartchef/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── recipes/                # Main app
│   ├── db.py              # MongoDB operations
│   ├── views.py           # Django views
│   ├── urls.py            # URL routes
│   └── context_processors.py
├── templates/              # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── recipes.html
│   ├── recipe_detail.html
│   ├── my_recipes.html
│   ├── add_recipe.html
│   ├── edit_recipe.html
│   ├── login.html
│   ├── register.html
│   └── profile.html
├── static/
│   ├── css/               # Stylesheets
│   │   ├── style.css
│   │   ├── variables.css
│   │   ├── components.css
│   │   ├── pages.css
│   │   ├── forms.css
│   │   └── responsive.css
│   ├── js/
│   │   └── main.js
│   └── images/            # Static images
├── media/                 # User uploads
│   └── recipes/
├── manage.py
├── requirements.txt
└── README.md
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB Atlas account (or local MongoDB)

### Step 1: Clone & Navigate
```bash
cd SmartChef
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Mac/Linux
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
Create a `.env` file (copy from `.env.example`):
```env
# MongoDB Atlas Connection
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/smartchef

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Step 5: Run the Server
```bash
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser 🎉

## 🗄️ Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "username": "ravi",
  "email": "ravi@email.com",
  "password": "hashed_password",
  "language": "en",
  "theme": "light",
  "favorites": []
}
```

### Recipes Collection
```json
{
  "_id": "ObjectId",
  "title": "Paneer Butter Masala",
  "category": "veg",
  "ingredients": ["Paneer", "Butter", "Tomato"],
  "steps": ["Heat pan", "Add butter", ...],
  "prep_time": "15 mins",
  "cook_time": "30 mins",
  "servings": 4,
  "image": "/media/recipes/image.jpg",
  "created_by": "user_id",
  "created_at": "timestamp",
  "likes": 0,
  "views": 0
}
```

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/recipes/` | All recipes |
| GET | `/recipe/<id>/` | Recipe detail |
| GET | `/my-recipes/` | User's recipes |
| GET/POST | `/add-recipe/` | Add new recipe |
| GET/POST | `/edit-recipe/<id>/` | Edit recipe |
| POST | `/delete-recipe/<id>/` | Delete recipe |
| GET/POST | `/login/` | User login |
| GET/POST | `/register/` | User registration |
| GET | `/logout/` | User logout |
| GET | `/profile/` | User profile |
| POST | `/settings/update/` | Update settings |
| GET | `/api/recipes/` | JSON API |

## 🎨 Screenshots

### Home Page
- Hero section with animated background
- Featured recipes grid
- Category navigation
- How it works section

### Recipes Page
- Search functionality
- Category filters (Veg, Non-Veg, Desserts, Drinks, Snacks)
- Beautiful recipe cards

### Profile Page
- User stats display
- Language selector (EN/HI/MR)
- Theme toggle (Light/Dark)

## 🔧 Configuration

### MongoDB Atlas Setup
1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a new cluster
3. Create database user
4. Get connection string
5. Add to `.env` file

### Sample Data
The app includes sample recipes that display when MongoDB is not connected:
- Paneer Butter Masala (Veg)
- Chicken Biryani (Non-Veg)
- Mango Lassi (Drinks)
- Gulab Jamun (Desserts)

## 🌍 Multi-Language Support

SmartChef supports 3 languages:
- 🇬🇧 **English** (Default)
- 🇮🇳 **Hindi** (हिंदी)
- 🇮🇳 **Marathi** (मराठी)

Users can change language from their profile settings.

## 🌙 Theme Support

- **Light Mode** ☀️ - Clean, bright interface
- **Dark Mode** 🌙 - Easy on the eyes

Theme preference is saved per user when logged in.

## 📱 Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## 📄 License

This project is created for educational purposes.

---

## 👩‍💻 Developed By

**Roshani Chaurasiya**

---

© 2026 SmartChef. All rights reserved.






To run the SmartChef project, you need to follow these steps in your terminal (make sure you are in the project folder SmartChef):

1. Create a Virtual Environment (Optional but recommended)
python -m venv venv
2. Activate the Virtual Environment
# On Windows:
venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
4. Run the Development Server
python manage.py runserver
Once the server is running, open http://127.0.0.1:8000/ in your browser.