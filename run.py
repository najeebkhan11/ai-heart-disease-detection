import uvicorn
import sys
import webbrowser
import threading
import time

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("=" * 60)
    print("🫀  AI Heart Disease Detection & Clinical Screening System")
    print("🚀  Starting server on http://localhost:8000")
    print("📖  Swagger API Docs: http://localhost:8000/docs")
    print("=" * 60)
    
    # Auto-open browser in background
    if "--no-browser" not in sys.argv:
        threading.Thread(target=open_browser, daemon=True).start()
        
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
