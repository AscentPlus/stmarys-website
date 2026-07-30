from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.core.cache import cache
from .models import WebsiteSetting, AboutSection, AcademicHighlight, Achievement, Facility, Event, Announcement, GalleryAlbum, ContactMessage
from .validators import validate_image_file, validate_pdf_file

class PublicWebsiteTests(TestCase):
    def setUp(self):
        # Create singleton settings
        self.settings_obj = WebsiteSetting.objects.create(
            school_name="Test School",
            email="test@school.com",
            phone="123456"
        )
        self.about_obj = AboutSection.objects.create(
            intro_title="Welcome",
            principal_name="Principal"
        )
        
    def test_home_page_load(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test School")
        
    def test_sitemap_xml_load(self):
        response = self.client.get(reverse('sitemap_xml'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
        self.assertIn(b'stmarysemschool.in', response.content)

    def test_robots_txt_load(self):
        response = self.client.get(reverse('robots_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertIn(b'Disallow: /admin/', response.content)
        
    def test_contact_form_submission_success(self):
        payload = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Inquiry',
            'message': 'Hello there!',
            'website_url': '' # Honeypot blank
        }
        response = self.client.post(reverse('contact_submit'), data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'success': True,
            'message': 'Thank you! Your message has been sent successfully. We will get back to you soon.'
        })
        self.assertEqual(ContactMessage.objects.count(), 1)
        
    def test_contact_form_submission_honeypot_discarded(self):
        payload = {
            'name': 'Spam Bot',
            'email': 'spam@bot.com',
            'subject': 'Spam',
            'message': 'Spam link here',
            'website_url': 'http://malicious-spam-url.com' # Honeypot filled!
        }
        response = self.client.post(reverse('contact_submit'), data=payload)
        self.assertEqual(response.status_code, 200)
        # Returns success to spoof the bot, but does NOT create a ContactMessage
        self.assertJSONEqual(response.content, {
            'success': True,
            'message': 'Thank you! Your message has been sent successfully. We will get back to you soon.'
        })
        self.assertEqual(ContactMessage.objects.count(), 0)

class StaffCMSAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', password='password123', is_staff=True)
        self.regular_user = User.objects.create_user(username='regular', password='password123', is_staff=False)
        cache.clear()
        
    def test_dashboard_anonymous_redirect(self):
        response = self.client.get(reverse('cms_dashboard'))
        self.assertRedirects(response, f"/cms/login/?next={reverse('cms_dashboard')}")
        
    def test_dashboard_non_staff_denied(self):
        self.client.login(username='regular', password='password123')
        response = self.client.get(reverse('cms_dashboard'))
        self.assertEqual(response.status_code, 302) # Redirects back to login or error
        
    def test_dashboard_staff_success(self):
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('cms_dashboard'))
        self.assertEqual(response.status_code, 200)
        
    def test_login_rate_limiting(self):
        login_url = reverse('cms_login')
        # Simulate 5 failed login attempts
        for i in range(5):
            response = self.client.post(login_url, {'username': 'admin', 'password': 'wrong_password'})
            self.assertEqual(response.status_code, 200)
            
        # The 6th attempt should return lockout message
        response = self.client.post(login_url, {'username': 'admin', 'password': 'wrong_password'})
        self.assertContains(response, "Too many failed login attempts")

class GalleryAlbumTests(TestCase):
    def test_unique_slug_generation(self):
        album1 = GalleryAlbum.objects.create(
            title="Sports Day 2026",
            date="2026-07-28",
            cover_image=SimpleUploadedFile("cover1.jpg", b"\xff\xd8\xff\xe0dummy_jpeg_data", content_type="image/jpeg")
        )
        self.assertEqual(album1.slug, "sports-day-2026")
        
        # Create second album with identical title
        album2 = GalleryAlbum.objects.create(
            title="Sports Day 2026",
            date="2026-07-28",
            cover_image=SimpleUploadedFile("cover2.jpg", b"\xff\xd8\xff\xe0dummy_jpeg_data", content_type="image/jpeg")
        )
        self.assertEqual(album2.slug, "sports-day-2026-2")

class FileValidationTests(TestCase):
    def test_valid_image(self):
        valid_jpeg = SimpleUploadedFile("test.jpg", b"\xff\xd8\xff\xe0test_data", content_type="image/jpeg")
        try:
            validate_image_file(valid_jpeg)
        except ValidationError:
            self.fail("validate_image_file raised ValidationError unexpectedly for valid JPEG.")
            
    def test_invalid_image_extension(self):
        invalid_ext = SimpleUploadedFile("test.exe", b"\xff\xd8\xff\xe0test_data", content_type="image/jpeg")
        with self.assertRaises(ValidationError):
            validate_image_file(invalid_ext)
            
    def test_invalid_image_magic_bytes(self):
        mismatched = SimpleUploadedFile("test.jpg", b"MZ\x90\x00\x03\x00\x00\x00executable", content_type="image/jpeg")
        with self.assertRaises(ValidationError):
            validate_image_file(mismatched)

    def test_valid_pdf(self):
        valid_pdf = SimpleUploadedFile("doc.pdf", b"%PDF-1.4\n%test_pdf_content", content_type="application/pdf")
        try:
            validate_pdf_file(valid_pdf)
        except ValidationError:
            self.fail("validate_pdf_file raised ValidationError unexpectedly for valid PDF.")
            
    def test_invalid_pdf_content(self):
        invalid_pdf = SimpleUploadedFile("doc.pdf", b"mismatched_text_here", content_type="application/pdf")
        with self.assertRaises(ValidationError):
            validate_pdf_file(invalid_pdf)
