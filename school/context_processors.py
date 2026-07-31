from .models import WebsiteSetting

def school_settings(request):
    return {
        'settings': WebsiteSetting.load()
    }
