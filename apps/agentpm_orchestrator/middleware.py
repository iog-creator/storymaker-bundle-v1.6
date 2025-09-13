"""
Envelope Gate Middleware - wraps all JSON responses to ensure envelope compliance.
"""

import json
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Any

from packages.pmagent.pmagent.envelope_validator import is_enveloped_response, _env_err


class EnvelopeGateMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures all JSON responses are properly enveloped.
    Non-enveloped responses are wrapped with NON_ENVELOPED_RESPONSE error.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Only process JSON responses
        if (response.headers.get("content-type", "").startswith("application/json") and 
            hasattr(response, 'body')):
            
            # Get the response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            try:
                # Parse the JSON response
                response_data = json.loads(body.decode('utf-8'))
                
                # Check if it's already enveloped
                if not is_enveloped_response(response_data):
                    # Wrap non-enveloped response with error envelope
                    error_envelope = _env_err(
                        code="NON_ENVELOPED_RESPONSE",
                        message="Response was not properly enveloped"
                    )
                    
                    # Create new response with enveloped error
                    return JSONResponse(
                        content=error_envelope,
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                # If we can't parse as JSON, let the original response through
                pass
        
        # Return original response if not JSON or already enveloped
        return response
