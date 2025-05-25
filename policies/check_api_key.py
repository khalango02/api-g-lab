expected_key = "secret123"

api_key = request.headers.get('X-Api-Key')

if api_key != expected_key:
    reject("Invalid or missing X-Api-Key header")
