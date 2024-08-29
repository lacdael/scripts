from dotenv import load_dotenv
from flask import Flask, make_response, jsonify
import jwt # pyjwt
import datetime
import os

app = Flask(__name__)

def getKey():
    with open("./private_key.pem",'rb') as f:
        k = f.read();
        return k;

@app.route('/api', methods=['GET'])
def get_content():
    content = "Hello, world!"
    data = {
        'payload':content,
        'exp':datetime.datetime.utcnow() +datetime.timedelta(minutes=30)    
        }
    mJWS = jwt.encode( data, getKey() , algorithm='RS256' ); 
    response = jsonify( mJWS );
    response.headers['Content-Type'] = 'application/json'

    return response

if __name__ == '__main__':
    app.run(debug=True,port=7070)


