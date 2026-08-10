import uvicorn

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Voice Server Wrapper is running!")
    print("Send a POST request to http://127.0.0.1:8000/start_call to begin.")
    print("="*50 + "\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
