import os
import sys
from langchain_community.document_loaders import PyMuPDFLoader

# Fix the import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.segmentor import segment_text

def test_segmentor_with_pdf(pdf_path, chunk_size=300):
    """Test the custom segmentor with a PDF file"""
    print(f"Testing segmentor with PDF: {pdf_path}")
    print(f"Chunk size: {chunk_size}")
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"Error: File not found - {pdf_path}")
        return
    
    # Load the PDF
    print("Loading PDF...")
    try:
        loader = PyMuPDFLoader(pdf_path)
        docs = loader.load()
        print(f"Successfully loaded PDF with {len(docs)} pages")
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return
    
    # Extract text from the first few pages
    print("Processing first 3 pages (or all if fewer)...")
    pages_to_process = min(3, len(docs))
    
    for i in range(pages_to_process):
        page_content = docs[i].page_content
        print(f"\n--- Page {i+1} ---")
        print(f"Original page length: {len(page_content)} characters")
        
        # Test the segmentor
        try:
            chunks = segment_text(page_content, chunk_size)
            print(f"Segmented into {len(chunks)} chunks")
            
            # Display the first few chunks
            chunks_to_show = min(3, len(chunks))
            for j in range(chunks_to_show):
                print(f"\nChunk {j+1}/{len(chunks)} (length: {len(chunks[j])}):")
                print(f"{chunks[j][:100]}..." if len(chunks[j]) > 100 else chunks[j])
                
        except Exception as e:
            print(f"Error during segmentation: {e}")

if __name__ == "__main__":
    # Use the provided PDF path or a default one
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = r"C:\Users\Ylon\Desktop\EduNova\example\cp07-样章示例-TensorFlow.js应用开发.pdf"
    
    test_segmentor_with_pdf(pdf_path) 