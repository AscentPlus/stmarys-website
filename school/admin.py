from django.contrib import admin
from .models import (
    WebsiteSetting, AboutSection, AcademicHighlight, Achievement,
    Facility, Event, EventImage, Announcement, GalleryAlbum, GalleryPhoto, ContactMessage
)

# Inline models
class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1

class GalleryPhotoInline(admin.TabularInline):
    model = GalleryPhoto
    extra = 1

# ModelAdmin classes
@admin.register(WebsiteSetting)
class WebsiteSettingAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'email', 'phone')
    
@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ('intro_title', 'principal_name')

@admin.register(AcademicHighlight)
class AcademicHighlightAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_class', 'order')
    list_editable = ('order',)
    ordering = ('order',)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'value', 'order')
    list_editable = ('order',)
    ordering = ('order',)

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)
    ordering = ('order',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_published', 'created_at')
    list_filter = ('is_published', 'date')
    search_fields = ('title', 'description')
    ordering = ('-date',)
    inlines = [EventImageInline]

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date', 'is_pinned', 'is_published')
    list_filter = ('category', 'is_pinned', 'is_published', 'date')
    search_fields = ('title', 'description')
    list_editable = ('is_pinned', 'is_published')
    ordering = ('-is_pinned', '-date')

@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'slug')
    search_fields = ('title', 'description')
    ordering = ('-date',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GalleryPhotoInline]

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
