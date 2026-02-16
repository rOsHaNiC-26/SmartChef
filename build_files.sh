#!/bin/bash
# Build script for Vercel deployment

echo "🔧 Installing dependencies..."
pip install -r requirements.txt

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed successfully!"
