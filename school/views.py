from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Prefetch

from .models import (
    WebsiteSetting, AboutSection, AcademicHighlight, Achievement,
    Facility, Event, EventImage, Announcement, GalleryAlbum, GalleryPhoto, ContactMessage
)
from .forms import (
    WebsiteSettingForm, AboutSectionForm, AcademicHighlightForm,
    AchievementForm, FacilityForm, EventForm, AnnouncementForm, GalleryAlbumForm, ContactForm,
    StyledPasswordChangeForm
)

# Helper decorator for CMS access
def staff_required(view_func):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='/cms/login/'
    )
    return actual_decorator(view_func)


# ==========================================
# PUBLIC VIEWS
# ==========================================

def home_view(request):
    settings = WebsiteSetting.load()
    about = AboutSection.load()
    highlights = AcademicHighlight.objects.all()
    achievements = Achievement.objects.all()
    facilities = Facility.objects.all()
    
    # Events: show published events, order by date desc
    events = Event.objects.filter(is_published=True).prefetch_related('images')[:6]
    
    # Announcements: latest published announcements
    announcements_all = Announcement.objects.filter(is_published=True)
    pinned_announcements = announcements_all.filter(is_pinned=True)
    regular_announcements = announcements_all.filter(is_pinned=False)[:8]
    
    # Gallery: fetch albums with their photos
    albums = GalleryAlbum.objects.all().prefetch_related('photos')[:8]
    
    # Contact Form
    contact_form = ContactForm()
    
    context = {
        'settings': settings,
        'about': about,
        'highlights': highlights,
        'achievements': achievements,
        'facilities': facilities,
        'events': events,
        'pinned_announcements': pinned_announcements,
        'regular_announcements': regular_announcements,
        'albums': albums,
        'contact_form': contact_form,
    }
    return render(request, 'school/home.html', context)


@require_POST
def contact_submit(request):
    # Spam protection: Honeypot check
    if request.POST.get('website_url', '').strip():
        # Silent discard, return dummy success to spambot
        return JsonResponse({
            'success': True,
            'message': 'Thank you! Your message has been sent successfully. We will get back to you soon.'
        })
        
    form = ContactForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({
            'success': True,
            'message': 'Thank you! Your message has been sent successfully. We will get back to you soon.'
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors.get_json_data()
        })


# ==========================================
# CMS AUTHENTICATION
# ==========================================

from django.core.cache import cache

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_login_lockout_key(username, ip):
    return f"lockout_{username}_{ip}"

def get_login_attempts_key(username, ip):
    return f"attempts_{username}_{ip}"


def cms_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('cms_dashboard')
        
    ip = get_client_ip(request)
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        lockout_key = get_login_lockout_key(username, ip)
        attempts_key = get_login_attempts_key(username, ip)
        
        # Check lockout
        if cache.get(lockout_key):
            messages.error(request, "Too many failed login attempts. Account locked temporarily for 15 minutes.")
            form = AuthenticationForm()
            return render(request, 'school/cms/login.html', {'form': form})
            
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                # Success: clear failure counters
                cache.delete(lockout_key)
                cache.delete(attempts_key)
                return redirect('cms_dashboard')
            else:
                messages.error(request, "Access denied. Staff access only.")
        else:
            # Record failure
            attempts = cache.get(attempts_key, 0) + 1
            cache.set(attempts_key, attempts, 900) # 15 min window
            if attempts >= 5:
                cache.set(lockout_key, True, 900) # lock for 15 min
                cache.delete(attempts_key)
                messages.error(request, "Too many failed login attempts. Account locked temporarily for 15 minutes.")
            else:
                messages.error(request, f"Invalid username or password. ({5 - attempts} attempts remaining)")
    else:
        form = AuthenticationForm()
        
    return render(request, 'school/cms/login.html', {'form': form})


def cms_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')


@staff_required
def cms_change_password(request):
    if request.method == 'POST':
        form = StyledPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Your password has been changed successfully!")
            return redirect('cms_edit_settings')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StyledPasswordChangeForm(user=request.user)
        
    return render(request, 'school/cms/change_password.html', {
        'form': form,
        'current_page': 'settings'  # keep active settings tab highlighted or none
    })



# ==========================================
# CMS DASHBOARD & GENERAL SETTINGS
# ==========================================

@staff_required
def cms_dashboard(request):
    unread_msg_count = ContactMessage.objects.filter(is_read=False).count()
    total_events = Event.objects.count()
    total_announcements = Announcement.objects.count()
    total_albums = GalleryAlbum.objects.count()
    
    recent_messages = ContactMessage.objects.all()[:5]
    recent_events = Event.objects.all()[:3]
    
    context = {
        'unread_msg_count': unread_msg_count,
        'total_events': total_events,
        'total_announcements': total_announcements,
        'total_albums': total_albums,
        'recent_messages': recent_messages,
        'recent_events': recent_events,
        'current_page': 'dashboard'
    }
    return render(request, 'school/cms/dashboard.html', context)


@staff_required
def cms_edit_settings(request):
    settings = WebsiteSetting.load()
    if request.method == 'POST':
        form = WebsiteSettingForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Website settings updated successfully.")
            return redirect('cms_edit_settings')
    else:
        form = WebsiteSettingForm(instance=settings)
    
    return render(request, 'school/cms/edit_settings.html', {
        'form': form,
        'settings': settings,
        'current_page': 'settings'
    })


# ==========================================
# CMS ABOUT US (About Section & Multi Items)
# ==========================================

def get_about_edit_context(request, **kwargs):
    about = AboutSection.load()
    highlights = AcademicHighlight.objects.all()
    achievements = Achievement.objects.all()
    facilities = Facility.objects.all()
    
    context = {
        'form': AboutSectionForm(instance=about),
        'about': about,
        'highlights': highlights,
        'achievements': achievements,
        'facilities': facilities,
        'highlight_form': AcademicHighlightForm(),
        'achievement_form': AchievementForm(),
        'facility_form': FacilityForm(),
        'current_page': 'about'
    }
    context.update(kwargs)
    return context


@staff_required
def cms_edit_about(request):
    about = AboutSection.load()
    
    if request.method == 'POST' and 'about_submit' in request.POST:
        form = AboutSectionForm(request.POST, request.FILES, instance=about)
        if form.is_valid():
            form.save()
            messages.success(request, "About Us sections updated successfully.")
            return redirect('cms_edit_about')
        else:
            messages.error(request, "Please correct the errors in the form below.")
            return render(request, 'school/cms/edit_about.html', get_about_edit_context(request, form=form))
    else:
        form = AboutSectionForm(instance=about)
        
    return render(request, 'school/cms/edit_about.html', get_about_edit_context(request, form=form))


# --- HIGHLIGHTS ---
@staff_required
def cms_add_highlight(request):
    if request.method == 'POST':
        form = AcademicHighlightForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Academic Highlight added.")
            return redirect('cms_edit_about')
        else:
            messages.error(request, "Failed to add highlight. Please check the fields below.")
            context = get_about_edit_context(
                request,
                highlight_form=form,
                open_modal='highlightModal',
                highlight_form_action=reverse('cms_add_highlight')
            )
            return render(request, 'school/cms/edit_about.html', context)
    return redirect('cms_edit_about')


@staff_required
def cms_edit_highlight(request, pk):
    highlight = get_object_or_404(AcademicHighlight, pk=pk)
    if request.method == 'POST':
        form = AcademicHighlightForm(request.POST, instance=highlight)
        if form.is_valid():
            form.save()
            messages.success(request, "Academic Highlight updated.")
            return redirect('cms_edit_about')
        else:
            messages.error(request, "Failed to update highlight. Please check the fields below.")
            context = get_about_edit_context(
                request,
                highlight_form=form,
                open_modal='highlightModal',
                highlight_form_action=reverse('cms_edit_highlight', args=[pk])
            )
            return render(request, 'school/cms/edit_about.html', context)
    return redirect('cms_edit_about')


@staff_required
@require_POST
def cms_delete_highlight(request, pk):
    highlight = get_object_or_404(AcademicHighlight, pk=pk)
    highlight.delete()
    messages.success(request, "Academic Highlight deleted.")
    return redirect('cms_edit_about')


# --- ACHIEVEMENTS ---
@staff_required
def cms_add_achievement(request):
    if request.method == 'POST':
        form = AchievementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Achievement added.")
            return redirect('cms_edit_about')
        else:
            messages.error(request, "Failed to add achievement. Please check the fields below.")
            context = get_about_edit_context(
                request,
                achievement_form=form,
                open_modal='achievementModal',
                achievement_form_action=reverse('cms_add_achievement')
            )
            return render(request, 'school/cms/edit_about.html', context)
    return redirect('cms_edit_about')


@staff_required
def cms_edit_achievement(request, pk):
    achievement = get_object_or_404(Achievement, pk=pk)
    if request.method == 'POST':
        form = AchievementForm(request.POST, instance=achievement)
        if form.is_valid():
            form.save()
            messages.success(request, "Achievement updated.")
            return redirect('cms_edit_about')
        else:
            messages.error(request, "Failed to update achievement. Please check the fields below.")
            context = get_about_edit_context(
                request,
                achievement_form=form,
                open_modal='achievementModal',
                achievement_form_action=reverse('cms_edit_achievement', args=[pk])
            )
            return render(request, 'school/cms/edit_about.html', context)
    return redirect('cms_edit_about')


@staff_required
@require_POST
def cms_delete_achievement(request, pk):
    achievement = get_object_or_404(Achievement, pk=pk)
    achievement.delete()
    messages.success(request, "Achievement deleted.")
    return redirect('cms_edit_about')


# --- FACILITIES ---
@staff_required
def cms_add_facility(request):
    if request.method == 'POST':
        form = FacilityForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Facility added.")
            return redirect('cms_edit_about')
        else:
            messages.error(request, "Failed to add facility. Please check the fields below.")
            context = get_about_edit_context(
                request,
                facility_form=form,
                open_modal='facilityModal',
                facility_form_action=reverse('cms_add_facility')
            )
            return render(request, 'school/cms/edit_about.html', context)
    return redirect('cms_edit_about')


@staff_required
def cms_edit_facility(request, pk):
    facility = get_object_or_404(Facility, pk=pk)
    if request.method == 'POST':
        form = FacilityForm(request.POST, request.FILES, instance=facility)
        if form.is_valid():
            form.save()
            messages.success(request, "Facility updated.")
            return redirect('cms_edit_about')
        else:
            messages.error(request, "Failed to update facility. Please check the fields below.")
            context = get_about_edit_context(
                request,
                facility_form=form,
                open_modal='facilityModal',
                facility_form_action=reverse('cms_edit_facility', args=[pk])
            )
            return render(request, 'school/cms/edit_about.html', context)
    return redirect('cms_edit_about')


@staff_required
@require_POST
def cms_delete_facility(request, pk):
    facility = get_object_or_404(Facility, pk=pk)
    facility.delete()
    messages.success(request, "Facility deleted.")
    return redirect('cms_edit_about')


# ==========================================
# CMS EVENTS
# ==========================================

@staff_required
def cms_manage_events(request):
    events_list = Event.objects.all()
    paginator = Paginator(events_list, 20)
    page_number = request.GET.get('page')
    events = paginator.get_page(page_number)
    return render(request, 'school/cms/manage_events.html', {
        'events': events,
        'current_page': 'events'
    })


@staff_required
def cms_add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            # Handle additional photos
            additional_photos = request.FILES.getlist('additional_photos')
            for f in additional_photos:
                EventImage.objects.create(event=event, image=f)
            messages.success(request, f"Event '{event.title}' created.")
            return redirect('cms_manage_events')
    else:
        form = EventForm()
    
    return render(request, 'school/cms/event_form.html', {
        'form': form,
        'action': 'Add',
        'current_page': 'events'
    })


@staff_required
def cms_edit_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            event = form.save()
            # Handle new additional photos
            additional_photos = request.FILES.getlist('additional_photos')
            for f in additional_photos:
                EventImage.objects.create(event=event, image=f)
            messages.success(request, f"Event '{event.title}' updated.")
            return redirect('cms_manage_events')
    else:
        form = EventForm(instance=event)
        
    return render(request, 'school/cms/event_form.html', {
        'form': form,
        'event': event,
        'action': 'Edit',
        'current_page': 'events'
    })


@staff_required
@require_POST
def cms_delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.delete()
    messages.success(request, "Event deleted successfully.")
    return redirect('cms_manage_events')


@staff_required
@require_POST
def cms_delete_event_photo(request, pk):
    img = get_object_or_404(EventImage, pk=pk)
    event_id = img.event.id
    img.delete()
    messages.success(request, "Additional photo removed.")
    return redirect('cms_edit_event', pk=event_id)


# ==========================================
# CMS ANNOUNCEMENTS
# ==========================================

@staff_required
def cms_manage_announcements(request):
    announcements_list = Announcement.objects.all()
    paginator = Paginator(announcements_list, 20)
    page_number = request.GET.get('page')
    announcements = paginator.get_page(page_number)
    return render(request, 'school/cms/manage_announcements.html', {
        'announcements': announcements,
        'current_page': 'announcements'
    })


@staff_required
def cms_add_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save()
            messages.success(request, f"Announcement '{announcement.title}' added.")
            return redirect('cms_manage_announcements')
    else:
        form = AnnouncementForm()
    return render(request, 'school/cms/announcement_form.html', {
        'form': form,
        'action': 'Add',
        'current_page': 'announcements'
    })


@staff_required
def cms_edit_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, f"Announcement '{announcement.title}' updated.")
            return redirect('cms_manage_announcements')
    else:
        form = AnnouncementForm(instance=announcement)
    return render(request, 'school/cms/announcement_form.html', {
        'form': form,
        'announcement': announcement,
        'action': 'Edit',
        'current_page': 'announcements'
    })


@staff_required
@require_POST
def cms_delete_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    announcement.delete()
    messages.success(request, "Announcement deleted successfully.")
    return redirect('cms_manage_announcements')


# ==========================================
# CMS GALLERY
# ==========================================

@staff_required
def cms_manage_gallery(request):
    albums_list = GalleryAlbum.objects.all().prefetch_related('photos')
    paginator = Paginator(albums_list, 20)
    page_number = request.GET.get('page')
    albums = paginator.get_page(page_number)
    return render(request, 'school/cms/manage_gallery.html', {
        'albums': albums,
        'current_page': 'gallery'
    })


@staff_required
def cms_add_album(request):
    if request.method == 'POST':
        form = GalleryAlbumForm(request.POST, request.FILES)
        if form.is_valid():
            album = form.save()
            # Upload photos
            photos = request.FILES.getlist('album_photos')
            for f in photos:
                GalleryPhoto.objects.create(album=album, image=f)
            messages.success(request, f"Album '{album.title}' created.")
            return redirect('cms_manage_gallery')
    else:
        form = GalleryAlbumForm()
    return render(request, 'school/cms/album_form.html', {
        'form': form,
        'action': 'Add',
        'current_page': 'gallery'
    })


@staff_required
def cms_edit_album(request, pk):
    album = get_object_or_404(GalleryAlbum, pk=pk)
    if request.method == 'POST':
        form = GalleryAlbumForm(request.POST, request.FILES, instance=album)
        if form.is_valid():
            album = form.save()
            # Upload new photos
            photos = request.FILES.getlist('album_photos')
            for f in photos:
                GalleryPhoto.objects.create(album=album, image=f)
            messages.success(request, f"Album '{album.title}' updated.")
            return redirect('cms_manage_gallery')
    else:
        form = GalleryAlbumForm(instance=album)
    return render(request, 'school/cms/album_form.html', {
        'form': form,
        'album': album,
        'action': 'Edit',
        'current_page': 'gallery'
    })


@staff_required
@require_POST
def cms_delete_album(request, pk):
    album = get_object_or_404(GalleryAlbum, pk=pk)
    album.delete()
    messages.success(request, "Album deleted successfully.")
    return redirect('cms_manage_gallery')


@staff_required
@require_POST
def cms_delete_gallery_photo(request, pk):
    photo = get_object_or_404(GalleryPhoto, pk=pk)
    album_id = photo.album.id
    photo.delete()
    messages.success(request, "Photo removed from album.")
    return redirect('cms_edit_album', pk=album_id)


# ==========================================
# CMS CONTACT MESSAGES
# ==========================================

@staff_required
def cms_view_messages(request):
    messages_list = ContactMessage.objects.all()
    paginator = Paginator(messages_list, 20)
    page_number = request.GET.get('page')
    contact_messages = paginator.get_page(page_number)
    return render(request, 'school/cms/view_messages.html', {
        'contact_messages': contact_messages,
        'current_page': 'messages'
    })


@staff_required
def cms_read_message(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save()
    return render(request, 'school/cms/message_detail.html', {
        'msg': msg,
        'current_page': 'messages'
    })


@staff_required
@require_POST
def cms_delete_message(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    messages.success(request, "Message deleted.")
    return redirect('cms_view_messages')


def sitemap_view(request):
    from django.http import HttpResponse
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://stmarysemschool.in/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""
    return HttpResponse(xml_content, content_type="application/xml")


def robots_view(request):
    from django.http import HttpResponse
    content = """User-agent: *
Allow: /
Disallow: /cms/
Disallow: /admin/
Sitemap: https://stmarysemschool.in/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")
