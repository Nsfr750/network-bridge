import os
import sys
import tkinter as tk
import traceback

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("Python path:", sys.path)

try:
    # Import struttura modules using relative imports
    from struttura import logger
    from app.bridge import NetworkBridgeApp
    print("Successfully imported all modules")
except ImportError as e:
    print(f"Error importing modules: {e}")
    traceback.print_exc()
    sys.exit(1)

def setup_global_exception_logging():
    """Set up global exception handling"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        import logging
        logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = handle_exception

def main():
    print("Starting main function")
    try:
        # Set up global exception handling
        setup_global_exception_logging()
        print("Global exception handling set up")
        
        # Create and run the application
        print("Creating root window")
        root = tk.Tk()
        print("Root window created")
        
        print("Creating NetworkBridgeApp")
        app = NetworkBridgeApp(root)
        print("NetworkBridgeApp created")
        
        print("Starting main loop")
        root.mainloop()
        print("Main loop ended")
        
    except Exception as e:
        print(f"Error in main: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    print("Starting application")
    main()
    print("Application ended")
