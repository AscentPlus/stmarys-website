class ContentSecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Build strict Content Security Policy directives
        csp_directives = [
            "default-src 'self'",
            "base-uri 'self'",
            "object-src 'none'",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "manifest-src 'self'",
            "worker-src 'self'",
            "media-src 'self'",
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com",
            "img-src 'self' data: blob:",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com",
            "script-src 'self' https://cdnjs.cloudflare.com",
            "connect-src 'self'",
            "frame-src 'self' https://www.google.com https://www.google.co.in",
        ]
        
        response["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # Hardened standard security headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["X-XSS-Protection"] = "0"
        
        # Cross-Origin Policies
        response["Cross-Origin-Opener-Policy"] = "same-origin"
        response["Cross-Origin-Resource-Policy"] = "same-origin"
        response["Cross-Origin-Embedder-Policy"] = "unsafe-none"
        
        # Permissions Policy
        response["Permissions-Policy"] = (
            "geolocation=(), "
            "camera=(), "
            "microphone=(), "
            "payment=(), "
            "usb=(), "
            "accelerometer=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "interest-cohort=(), "
            "fullscreen=(self)"
        )
        
        return response
