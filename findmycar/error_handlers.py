"""
Error handling and custom error pages for production
Provides structured error responses and logging
"""
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import logging
import uuid
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")

def generate_request_id() -> str:
    """Generate unique request ID for error tracking"""
    return str(uuid.uuid4())[:8]

async def handle_404_error(request: Request, exc: HTTPException):
    """Handle 404 Not Found errors"""
    request_id = generate_request_id()
    
    # Log the 404 error
    logger.warning(f"404 Error - Request ID: {request_id}, Path: {request.url.path}, IP: {request.client.host}")
    
    # Return JSON for API requests
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": "The requested resource was not found",
                "request_id": request_id,
                "status_code": 404
            }
        )
    
    # Return HTML page for web requests
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request, "request_id": request_id},
        status_code=404
    )

async def handle_500_error(request: Request, exc: Exception):
    """Handle 500 Internal Server Error"""
    request_id = generate_request_id()
    
    # Log the error with full traceback
    logger.error(
        f"500 Error - Request ID: {request_id}, Path: {request.url.path}, IP: {request.client.host}",
        exc_info=True
    )
    
    # Return JSON for API requests
    if request.url.path.startswith("/api/"):
        error_response = {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "request_id": request_id,
            "status_code": 500
        }
        
        # In development, include more details
        import os
        if os.getenv("ENVIRONMENT", "development") == "development":
            error_response["details"] = str(exc)
            error_response["traceback"] = traceback.format_exc()
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )
    
    # Return HTML page for web requests
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request, "request_id": request_id},
        status_code=500
    )

async def handle_422_error(request: Request, exc: HTTPException):
    """Handle 422 Validation Error"""
    request_id = generate_request_id()
    
    logger.warning(f"422 Validation Error - Request ID: {request_id}, Path: {request.url.path}, IP: {request.client.host}")
    
    # Return JSON for all validation errors
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "The request data is invalid",
            "details": exc.detail if hasattr(exc, 'detail') else "Invalid input",
            "request_id": request_id,
            "status_code": 422
        }
    )

async def handle_429_error(request: Request, exc: HTTPException):
    """Handle 429 Rate Limit Error"""
    request_id = generate_request_id()
    
    logger.warning(f"429 Rate Limit - Request ID: {request_id}, Path: {request.url.path}, IP: {request.client.host}")
    
    # Return JSON for API requests
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate Limit Exceeded",
                "message": "Too many requests. Please try again later.",
                "request_id": request_id,
                "status_code": 429
            }
        )
    
    # Return error message for web requests (redirect to home with error)
    from fastapi.responses import RedirectResponse
    return RedirectResponse(
        url=f"/?error=Rate limit exceeded. Please wait before trying again.",
        status_code=302
    )

async def handle_401_error(request: Request, exc: HTTPException):
    """Handle 401 Unauthorized Error"""
    request_id = generate_request_id()
    
    logger.warning(f"401 Unauthorized - Request ID: {request_id}, Path: {request.url.path}, IP: {request.client.host}")
    
    return JSONResponse(
        status_code=401,
        content={
            "error": "Unauthorized",
            "message": "Authentication required",
            "request_id": request_id,
            "status_code": 401
        }
    )

async def handle_403_error(request: Request, exc: HTTPException):
    """Handle 403 Forbidden Error"""
    request_id = generate_request_id()
    
    logger.warning(f"403 Forbidden - Request ID: {request_id}, Path: {request.url.path}, IP: {request.client.host}")
    
    return JSONResponse(
        status_code=403,
        content={
            "error": "Forbidden",
            "message": "Access denied",
            "request_id": request_id,
            "status_code": 403
        }
    )

class ErrorLoggingMiddleware:
    """Middleware to add request IDs and enhanced error logging"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Add request ID to scope
            scope["request_id"] = generate_request_id()
            
            # Log request start
            path = scope.get("path", "")
            method = scope.get("method", "")
            client_ip = None
            
            if scope.get("client"):
                client_ip = scope["client"][0]
            
            logger.debug(f"Request started - ID: {scope['request_id']}, {method} {path}, IP: {client_ip}")
        
        await self.app(scope, receive, send)

def setup_error_handlers(app):
    """Set up all error handlers for the FastAPI app"""
    
    # Add custom error handlers
    app.add_exception_handler(404, handle_404_error)
    app.add_exception_handler(500, handle_500_error)
    app.add_exception_handler(422, handle_422_error)
    app.add_exception_handler(429, handle_429_error)
    app.add_exception_handler(401, handle_401_error)
    app.add_exception_handler(403, handle_403_error)
    
    # Add error logging middleware
    app.add_middleware(ErrorLoggingMiddleware)
    
    logger.info("Error handlers and middleware configured")

# Security headers middleware
class SecurityHeadersMiddleware:
    """Add security headers to all responses"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                
                # Add security headers
                security_headers = {
                    b"x-content-type-options": b"nosniff",
                    b"x-frame-options": b"DENY",
                    b"x-xss-protection": b"1; mode=block",
                    b"strict-transport-security": b"max-age=31536000; includeSubDomains",
                    b"referrer-policy": b"strict-origin-when-cross-origin",
                    b"content-security-policy": b"default-src 'self'; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://stackpath.bootstrapcdn.com; script-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https://cdnjs.cloudflare.com;"
                }
                
                headers.update(security_headers)
                message["headers"] = list(headers.items())
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)