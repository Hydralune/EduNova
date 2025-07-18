import os
import sys
import argparse
from dotenv import load_dotenv

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import RAG query functions
from rag.rag_query import rag_query, rag_query_stream

def test_rag_chat(course_id, query=None, stream=False):
    """
    Test the RAG chat functionality with a given course knowledge base
    
    Args:
        course_id: The ID of the course knowledge base to use
        query: The query to ask (if None, will prompt the user for input)
        stream: Whether to use streaming response
    """
    print(f"Testing RAG chat with knowledge base: {course_id}")
    
    # Check if knowledge base exists
    kb_path = os.path.join("uploads/knowledge_base", course_id)
    if not os.path.exists(kb_path):
        print(f"Error: Knowledge base not found at {kb_path}")
        return
    
    print(f"Knowledge base found at: {kb_path}")
    
    # Interactive chat loop
    while True:
        # Get query from argument or user input
        if query:
            user_query = query
            # Only use the provided query once, then switch to interactive mode
            query = None
        else:
            user_query = input("\n请输入您的问题 (输入'exit'退出): ")
            
        if user_query.lower() in ['exit', 'quit', '退出']:
            print("感谢使用，再见！")
            break
        
        print("\n正在查询知识库...")
        
        try:
            # Use streaming or regular response based on the flag
            if stream:
                print("\n回答: ", end="")
                for chunk in rag_query_stream(user_query, course_id):
                    print(chunk, end="", flush=True)
                print("\n")
            else:
                response = rag_query(user_query, course_id)
                print("\n回答:")
                print(response)
                
        except Exception as e:
            print(f"查询过程中出错: {e}")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test RAG chat with a knowledge base")
    parser.add_argument("--course_id", help="The ID of the course knowledge base to use", 
                        default="test_course_f84787f9")  # Default to the last created test course
    parser.add_argument("--query", help="The initial query to ask")
    parser.add_argument("--stream", help="Use streaming response", action="store_true")
    
    args = parser.parse_args()
    
    # Run the test
    test_rag_chat(args.course_id, args.query, args.stream) 