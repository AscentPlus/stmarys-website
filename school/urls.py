from django.urls import path
from . import views

urlpatterns = [
    # Public Website Paths
    path('', views.home_view, name='home'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),

    # CMS Authentication
    path('cms/login/', views.cms_login, name='cms_login'),
    path('cms/logout/', views.cms_logout, name='cms_logout'),
    path('cms/password/', views.cms_change_password, name='cms_change_password'),

    # CMS Dashboard & Settings
    path('cms/', views.cms_dashboard, name='cms_dashboard'),
    path('cms/settings/', views.cms_edit_settings, name='cms_edit_settings'),

    # CMS About Us Sections & Components
    path('cms/about/', views.cms_edit_about, name='cms_edit_about'),
    path('cms/about/highlight/add/', views.cms_add_highlight, name='cms_add_highlight'),
    path('cms/about/highlight/edit/<int:pk>/', views.cms_edit_highlight, name='cms_edit_highlight'),
    path('cms/about/highlight/delete/<int:pk>/', views.cms_delete_highlight, name='cms_delete_highlight'),
    
    path('cms/about/achievement/add/', views.cms_add_achievement, name='cms_add_achievement'),
    path('cms/about/achievement/edit/<int:pk>/', views.cms_edit_achievement, name='cms_edit_achievement'),
    path('cms/about/achievement/delete/<int:pk>/', views.cms_delete_achievement, name='cms_delete_achievement'),
    
    path('cms/about/facility/add/', views.cms_add_facility, name='cms_add_facility'),
    path('cms/about/facility/edit/<int:pk>/', views.cms_edit_facility, name='cms_edit_facility'),
    path('cms/about/facility/delete/<int:pk>/', views.cms_delete_facility, name='cms_delete_facility'),

    # CMS Events
    path('cms/events/', views.cms_manage_events, name='cms_manage_events'),
    path('cms/events/add/', views.cms_add_event, name='cms_add_event'),
    path('cms/events/edit/<int:pk>/', views.cms_edit_event, name='cms_edit_event'),
    path('cms/events/delete/<int:pk>/', views.cms_delete_event, name='cms_delete_event'),
    path('cms/events/photo/delete/<int:pk>/', views.cms_delete_event_photo, name='cms_delete_event_photo'),

    # CMS Announcements
    path('cms/announcements/', views.cms_manage_announcements, name='cms_manage_announcements'),
    path('cms/announcements/add/', views.cms_add_announcement, name='cms_add_announcement'),
    path('cms/announcements/edit/<int:pk>/', views.cms_edit_announcement, name='cms_edit_announcement'),
    path('cms/announcements/delete/<int:pk>/', views.cms_delete_announcement, name='cms_delete_announcement'),

    # CMS Gallery Albums
    path('cms/gallery/', views.cms_manage_gallery, name='cms_manage_gallery'),
    path('cms/gallery/add/', views.cms_add_album, name='cms_add_album'),
    path('cms/gallery/edit/<int:pk>/', views.cms_edit_album, name='cms_edit_album'),
    path('cms/gallery/delete/<int:pk>/', views.cms_delete_album, name='cms_delete_album'),
    path('cms/gallery/photo/delete/<int:pk>/', views.cms_delete_gallery_photo, name='cms_delete_gallery_photo'),

    # CMS Messages
    path('cms/messages/', views.cms_view_messages, name='cms_view_messages'),
    path('cms/messages/read/<int:pk>/', views.cms_read_message, name='cms_read_message'),
    path('cms/messages/delete/<int:pk>/', views.cms_delete_message, name='cms_delete_message'),

    # SEO Paths
    path('sitemap.xml', views.sitemap_view, name='sitemap_xml'),
    path('robots.txt', views.robots_view, name='robots_txt'),
    path('llms.txt', views.llms_view, name='llms_txt'),
]
