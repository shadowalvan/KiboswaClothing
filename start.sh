#!/bin/bash

# Start script for Kiboswa CTF

echo "========================================="
echo "  KIBOSWA CTF - Docker Container"
echo "========================================="
echo ""

# Check if database exists
if [ ! -f "ctf_database.db" ]; then
    echo "📁 Creating database..."
    python -c "import sqlite3; conn = sqlite3.connect('ctf_database.db'); conn.close()"
    echo "✅ Database created"
fi

echo ""
echo "🚀 Starting Flask application..."
echo "🌐 Access at: http://localhost:5000"
echo "🔐 Admin Login: admin / admin123"
echo "👤 User Login: alvan / 1234"
echo ""
echo "📝 CTF Challenges available at: http://localhost:5000/challenges"
echo ""

# Run the application
python app.py