from flask import Flask, request, Response
import requests

app = Flask(__name__)

# Target backend server
BACKEND_URL = 'http://localhost:5001'

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy(path):
    # Forward the request to the backend
    url = f"{BACKEND_URL}/{path}"
    
    # Print request details for debugging
    print(f"Proxying request: {request.method} {url}")
    print(f"Headers: {request.headers}")
    
    # Handle OPTIONS requests directly
    if request.method == 'OPTIONS':
        response = Response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # Forward the request to the backend
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers={key: value for key, value in request.headers.items() if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            params=request.args,
            allow_redirects=False
        )
        
        # Create a Flask response object
        response = Response(resp.content, resp.status_code)
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        
        # Copy headers from the backend response
        for key, value in resp.headers.items():
            if key.lower() not in ['access-control-allow-origin', 'access-control-allow-headers', 'access-control-allow-methods']:
                response.headers[key] = value
                
        return response
    except Exception as e:
        print(f"Proxy error: {e}")
        return Response(f"Proxy error: {e}", 500)

if __name__ == '__main__':
    print("Starting CORS proxy server on port 8080...")
    print("Frontend should connect to http://localhost:8080/api")
    app.run(host='0.0.0.0', port=8080, debug=True) 