import os
import sqlite3

def check_users():
    db_path = os.path.join('database', 'eduNova.sqlite')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("User table doesn't exist in the database")
            return
        
        # Get all users
        cursor.execute('SELECT id, username, email, password_hash, role, is_active FROM user')
        users = cursor.fetchall()
        
        print(f"Found {len(users)} users:")
        for user in users:
            user_id, username, email, password_hash, role, is_active = user
            print(f"ID: {user_id}, Username: {username}, Email: {email}, Role: {role}, Active: {is_active}")
            print(f"  Password Hash: {password_hash[:20]}...")
            print("-" * 50)
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_users() 