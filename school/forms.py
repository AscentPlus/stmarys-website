from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from .models import (
    WebsiteSetting, AboutSection, AcademicHighlight, 
    Achievement, Facility, Event, Announcement, GalleryAlbum, ContactMessage
)

class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Check widget type to apply custom classes
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'form-control textarea-field',
                    'rows': 4,
                    'placeholder': field.label
                })
            elif isinstance(field.widget, (forms.FileInput, forms.ClearableFileInput)):
                field.widget.attrs.update({
                    'class': 'form-control-file'
                })
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'form-check-input'
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': 'form-control select-field'
                })
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({
                    'class': 'form-control date-field',
                    'type': 'date'
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-control text-field',
                    'placeholder': field.label
                })
        
        if self.is_bound:
            for field_name, field in self.fields.items():
                if self.errors.get(field_name):
                    existing_class = field.widget.attrs.get('class', '')
                    if 'is-invalid' not in existing_class:
                        field.widget.attrs.update({
                            'class': f"{existing_class} is-invalid"
                        })


class WebsiteSettingForm(StyledModelForm):
    class Meta:
        model = WebsiteSetting
        exclude = ['social_twitter']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'logo': forms.FileInput(),
            'hero_bg': forms.FileInput(),
        }


class AboutSectionForm(StyledModelForm):
    class Meta:
        model = AboutSection
        fields = '__all__'
        widgets = {
            'intro_content': forms.Textarea(attrs={'rows': 5}),
            'principal_message': forms.Textarea(attrs={'rows': 5}),
            'parallax_text': forms.Textarea(attrs={'rows': 2}),
            'intro_image': forms.FileInput(),
            'principal_image': forms.FileInput(),
            'parallax_bg': forms.FileInput(),
        }


class AcademicHighlightForm(StyledModelForm):
    class Meta:
        model = AcademicHighlight
        fields = ['title', 'description', 'icon_class', 'order']


class AchievementForm(StyledModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'value', 'description', 'order']


class FacilityForm(StyledModelForm):
    class Meta:
        model = Facility
        fields = ['title', 'description', 'image', 'order']
        widgets = {
            'image': forms.FileInput(),
        }


class EventForm(StyledModelForm):
    class Meta:
        model = Event
        fields = ['title', 'date', 'description', 'cover_image', 'is_published']
        widgets = {
            'cover_image': forms.FileInput(),
        }


class AnnouncementForm(StyledModelForm):
    class Meta:
        model = Announcement
        fields = ['category', 'title', 'date', 'description', 'pdf_file', 'is_pinned', 'is_published']


class GalleryAlbumForm(StyledModelForm):
    class Meta:
        model = GalleryAlbum
        fields = ['title', 'description', 'cover_image', 'date']
        widgets = {
            'cover_image': forms.FileInput(),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'form-field'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-field'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number (Optional)', 'class': 'form-field'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject', 'class': 'form-field'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your Message...', 'rows': 4, 'class': 'form-field'}),
        }


class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control text-field',
                'placeholder': field.label
            })
            
        if self.is_bound:
            for field_name, field in self.fields.items():
                if self.errors.get(field_name):
                    existing_class = field.widget.attrs.get('class', '')
                    if 'is-invalid' not in existing_class:
                        field.widget.attrs.update({
                            'class': f"{existing_class} is-invalid"
                        })

