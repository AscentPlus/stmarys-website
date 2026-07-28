class ContentSecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Build strict Content Security Policy directives
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'",
            "style-src 'self' 'unsafe-inline' fonts.googleapis.com cdnjs.cloudflare.com",
            "img-src 'self' data: *",  # Allow local media and external logos
            "font-src 'self' data: fonts.gstatic.com cdnjs.cloudflare.com",
            "frame-src 'self' *.google.com *.google.co.in",  # Support Google Maps embeds
            "connect-src 'self'",
        ]
        
        response["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # Hardened standard headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "SAMEORIGIN"
        response["Referrer-Policy"] = "same-origin"
        
        return response
