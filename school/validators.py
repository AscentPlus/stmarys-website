import os
from django.core.exceptions import ValidationError

def validate_image_file(file):
    # Limit size to 5MB
    max_size = 5 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError("Image file size cannot exceed 5MB.")
        
    ext = os.path.splitext(file.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    if ext not in valid_extensions:
        raise ValidationError("Allowed image formats are: JPG, JPEG, PNG, WEBP.")
        
    # Inspect magic bytes to prevent spoofing
    try:
        file.seek(0)
        header = file.read(16)
        file.seek(0) # Reset stream pointer
    except Exception:
        raise ValidationError("Unable to verify file headers. File might be corrupted.")
        
    is_png = header.startswith(b'\x89PNG\r\n\x1a\n')
    is_jpeg = header.startswith(b'\xff\xd8')
    is_webp = header.startswith(b'RIFF') and b'WEBP' in header[8:12]
    
    if not (is_png or is_jpeg or is_webp):
        raise ValidationError("Uploaded file is not a valid image format (JPEG, PNG, WEBP only) or has mismatched content type.")

def validate_pdf_file(file):
    # Limit size to 10MB
    max_size = 10 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError("PDF document size cannot exceed 10MB.")
        
    ext = os.path.splitext(file.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError("Only PDF documents (.pdf) are allowed.")
        
    # Inspect magic bytes to prevent spoofing
    try:
        file.seek(0)
        header = file.read(8)
        file.seek(0) # Reset stream pointer
    except Exception:
        raise ValidationError("Unable to verify document headers. File might be corrupted.")
        
    if not header.startswith(b'%PDF'):
        raise ValidationError("Uploaded file is not a valid PDF document.")
