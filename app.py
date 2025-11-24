from flask import Flask, request, make_response
import os

app = Flask(__name__)

# WARNING: This application contains intentional security vulnerabilities
# for DAST testing purposes. DO NOT deploy this to production!

@app.route('/')
def hello():
    # Get query parameter for reflected XSS on homepage
    query = request.args.get('q', '')

    # VULNERABLE: Multiple issues on the homepage itself
    # 1. Reflected XSS from query parameter
    # 2. Missing charset specification
    # 3. Vulnerable JavaScript library
    # 4. CORS misconfiguration

    response = make_response(f"""
    <html>
    <head>
        <title>Provenance Example - DAST Test App</title>
        <script src="https://code.jquery.com/jquery-1.8.0.min.js"></script>
    </head>
    <body>
        <h1>Hello from signed container!</h1>
        <p>This app contains intentional vulnerabilities for DAST testing.</p>
        <div>Search query: {query}</div>
        <form action="/" method="get">
            <input type="text" name="q" placeholder="Search...">
            <input type="submit" value="Search">
        </form>
        <ul>
            <li><a href="/search?q=test">Search Page</a></li>
            <li><a href="/cors">CORS Endpoint</a></li>
            <li><a href="/vulnerable-js">JavaScript Page</a></li>
            <li><a href="/no-content-type">No Content-Type</a></li>
            <li><a href="/duplicate-cookies">Duplicate Cookies</a></li>
        </ul>
    </body>
    </html>
    """)

    # VULNERABLE: Overly permissive CORS on homepage
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    return response

# Vulnerability 1: Reflected XSS (Dastardly WILL detect this)
@app.route('/search')
def search():
    query = request.args.get('q', '')
    # VULNERABLE: User input directly embedded in HTML without escaping
    # This is a reflected XSS vulnerability that Dastardly should detect
    html = f"""
    <html>
    <body>
        <h1>Search Results</h1>
        <p>You searched for: {query}</p>
        <p><a href="/">Back to home</a></p>
    </body>
    </html>
    """
    return html

# Vulnerability 2: CORS misconfiguration (Dastardly WILL detect this)
@app.route('/cors')
def cors_endpoint():
    response = make_response("""
    <html>
    <body>
        <h1>CORS Endpoint</h1>
        <p>This endpoint has overly permissive CORS settings.</p>
        <p><a href="/">Back to home</a></p>
    </body>
    </html>
    """)
    # VULNERABLE: Overly permissive CORS allowing any origin
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

# Vulnerability 3: Vulnerable JavaScript dependency (Dastardly WILL detect this)
@app.route('/vulnerable-js')
def vulnerable_js():
    # VULNERABLE: Using old vulnerable version of jQuery (1.8.0 has known XSS issues)
    return """
    <html>
    <head>
        <script src="https://code.jquery.com/jquery-1.8.0.min.js"></script>
    </head>
    <body>
        <h1>Page with Vulnerable JavaScript</h1>
        <p>This page includes jQuery 1.8.0 which has known vulnerabilities.</p>
        <p><a href="/">Back to home</a></p>
    </body>
    </html>
    """

# Vulnerability 4: Missing Content-Type (Dastardly WILL detect this)
@app.route('/no-content-type')
def no_content_type():
    # VULNERABLE: Response without Content-Type header
    response = make_response("<html><body><h1>No Content-Type</h1></body></html>")
    # Explicitly remove Content-Type if Flask sets it
    if 'Content-Type' in response.headers:
        del response.headers['Content-Type']
    return response

# Vulnerability 5: Duplicate cookies (Dastardly WILL detect this)
@app.route('/duplicate-cookies')
def duplicate_cookies():
    # VULNERABLE: Setting the same cookie multiple times
    response = make_response("""
    <html>
    <body>
        <h1>Duplicate Cookies</h1>
        <p>This response sets duplicate cookies.</p>
        <p><a href="/">Back to home</a></p>
    </body>
    </html>
    """)
    response.set_cookie('session_id', 'value1')
    response.set_cookie('session_id', 'value2')
    return response

@app.after_request
def add_headers(response):
    # Don't set charset in Content-Type to trigger "HTML does not specify charset"
    # Don't set multiple Content-Type values as that requires raw header manipulation
    return response

if __name__ == '__main__':
    # VULNERABLE: Debug mode should never be enabled in production
    app.run(host='0.0.0.0', port=8080, debug=True)
