# check_decorator.py
import inspect
from auth.utils import token_required

def analyze_decorator():
    print("🔍 Analyzing token_required decorator:")
    print("=" * 50)
    
    # Get the source code of the decorator
    try:
        source = inspect.getsource(token_required)
        print("Current token_required decorator source:")
        print(source)
        
        # Check if it passes user_role
        if 'user_role' in source:
            print("❌ ISSUE FOUND: decorator is passing 'user_role' parameter")
            print("💡 SOLUTION: Remove 'user_role=current_user.role' from the return statement")
        else:
            print("✅ Decorator looks correct - only passes current_user")
            
    except Exception as e:
        print(f"Error analyzing decorator: {e}")

if __name__ == "__main__":
    analyze_decorator()