import os
import sys
import sqlite3

# Add the parent directory to the path so we can import from backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def migrate_student_answers():
    """Add missing columns to student_answers table"""
    print("Starting migration for student_answers table...")
    
    # Get the database path
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
    db_path = os.path.join(db_dir, 'eduNova.sqlite')
    print(f"Database path: {db_path}")
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"ERROR: Database file not found at {db_path}")
        return
    
    # Connect to the database
    print(f"Connecting to database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the student_answers table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='student_answers'")
    if not cursor.fetchone():
        print("ERROR: student_answers table does not exist!")
        conn.close()
        return
    
    # Check if the question_scores column exists
    print("Checking table structure...")
    cursor.execute("PRAGMA table_info(student_answers)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"Existing columns: {column_names}")
    
    # Add question_scores column if it doesn't exist
    if 'question_scores' not in column_names:
        print("Adding question_scores column to student_answers table...")
        cursor.execute("ALTER TABLE student_answers ADD COLUMN question_scores TEXT")
        print("Added question_scores column successfully.")
    else:
        print("question_scores column already exists.")
    
    # Add question_feedback column if it doesn't exist
    if 'question_feedback' not in column_names:
        print("Adding question_feedback column to student_answers table...")
        cursor.execute("ALTER TABLE student_answers ADD COLUMN question_feedback TEXT")
        print("Added question_feedback column successfully.")
    else:
        print("question_feedback column already exists.")
    
    # Commit the changes
    print("Committing changes...")
    conn.commit()
    conn.close()
    
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate_student_answers() 