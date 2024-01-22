import sys
sys.path.append('C:\\Users\\s-msheng\\cs\\asp_3\\server\\lib')
# ^^^ IMPORTANT: DEVELOPMENT ONLY

from lib.flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    print("Received request at /")
    return {"message": "you have been issued the latest version of our premium virus. thank you for your downloads"}

app.run("localhost", 3999)