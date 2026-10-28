import time
from functools import wraps
from flask import request, jsonify, current_app

# Thread-safe enough for local development / in-memory store
_request_records = {}

def rate_limit(max_requests=15, window_seconds=60):
    """
    In-memory rate limiter decorator.
    Tracks client IP or optional identifier per sliding window.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Bypass rate limit during automated tests unless explicitly requested
            if current_app.config.get('TESTING') and not request.headers.get('X-Test-Rate-Limit'):
                return f(*args, **kwargs)

            # Determine client identity (X-Forwarded-For if proxied or remote_addr)
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown').split(',')[0].strip()
            key = f"{f.__name__}:{client_ip}"
            
            now = time.time()
            timestamps = _request_records.get(key, [])
            
            # Filter out timestamps outside window
            cutoff = now - window_seconds
            timestamps = [t for t in timestamps if t > cutoff]
            
            if len(timestamps) >= max_requests:
                retry_after = int(window_seconds - (now - timestamps[0])) + 1
                resp = jsonify({
                    'error': f'Too many requests. Please wait {max_requests} requests per {window_seconds}s limit. Try again in {retry_after}s.'
                })
                resp.status_code = 429
                resp.headers['Retry-After'] = str(retry_after)
                return resp
            
            timestamps.append(now)
            _request_records[key] = timestamps
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def reset_rate_limits():
    """Utility function to clear in-memory state in tests."""
    global _request_records
    _request_records.clear()

