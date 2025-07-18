import os
import sys
import uuid
import logging

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the process_document_with_progress function from create_db
from backend.rag.create_db import process_document_with_progress

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def progress_callback(progress, stage=None, message=None):
    """Simple progress callback function"""
    if stage and message:
        print(f"Progress: {progress:.1f}% - Stage: {stage} - {message}")
    else:
        print(f"Progress: {progress:.1f}%")

def test_create_db_with_pdf(pdf_path):
    """Test if create_db can process a PDF document using our segmentor"""
    print(f"Testing create_db with PDF: {pdf_path}")
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"Error: File not found - {pdf_path}")
        return
    
    # Create a temporary course ID for testing
    test_course_id = f"test_course_{uuid.uuid4().hex[:8]}"
    print(f"Using temporary course ID: {test_course_id}")
    
    try:
        # Process the document
        result = process_document_with_progress(
            course_id=test_course_id,
            file_path=pdf_path,
            progress_callback=progress_callback
        )
        
        if result:
            print(f"✅ Document processed successfully!")
            print(f"Knowledge base created at: uploads/knowledge_base/{test_course_id}")
        else:
            print("❌ Document processing failed")
            
    except Exception as e:
        print(f"❌ Error during document processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Use the provided PDF path or a default one
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = r"C:\Users\Ylon\Desktop\EduNova\example\cp07-样章示例-TensorFlow.js应用开发.pdf"
    
    test_create_db_with_pdf(pdf_path) 