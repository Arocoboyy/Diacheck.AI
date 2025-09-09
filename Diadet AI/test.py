import os
print("Current directory:", os.getcwd())
print("Files in directory:", os.listdir("."))
print("best.pt exists:", os.path.exists("best.pt"))

# Test buka file
try:
    with open("best.pt", "rb") as f:
        print("File dapat dibaca! Size:", f.seek(0, 2), "bytes")
except Exception as e:
    print("Error:", e)
