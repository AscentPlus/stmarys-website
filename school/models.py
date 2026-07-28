from django.db import models
from django.utils.text import slugify
from .validators import validate_image_file, validate_pdf_file

class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class WebsiteSetting(SingletonModel):
    school_name = models.CharField(max_length=200, default="St. Mary's Lower Primary School")
    school_motto = models.CharField(max_length=200, default="Nurturing Hearts, Inspiring Minds")
    logo = models.ImageField(upload_to='site/', blank=True, null=True, validators=[validate_image_file])
    hero_bg = models.ImageField(upload_to='site/', blank=True, null=True, validators=[validate_image_file])
    hero_heading = models.CharField(max_length=300, default="Learning is a Joyful Adventure")
    hero_cta_text = models.CharField(max_length=100, default="Explore Our World")
    hero_cta_link = models.CharField(max_length=100, default="#about")
    
    # Contact Info
    phone = models.CharField(max_length=100, default="+91 484 2345678")
    email = models.EmailField(default="info@stmaryslpschool.edu.in")
    address = models.TextField(default="St. Mary's LP School, Church Road, Ernakulam, Kerala, PIN - 682011")
    map_iframe = models.TextField(
        blank=True, 
        null=True,
        default='<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3929.5678910111!2d76.2811!3d9.9723" width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe>'
    )
    
    # Social Links
    social_facebook = models.URLField(blank=True, null=True, default="https://facebook.com")
    social_instagram = models.URLField(blank=True, null=True, default="https://instagram.com")
    social_youtube = models.URLField(blank=True, null=True, default="https://youtube.com")
    social_twitter = models.URLField(blank=True, null=True, default="https://twitter.com")

    def __str__(self):
        return "Website Settings"


class AboutSection(SingletonModel):
    # Introduction
    intro_title = models.CharField(max_length=200, default="Welcome to St. Mary's LP School")
    intro_content = models.TextField(default="For over five decades, St. Mary's LP School has been a guiding light in early childhood education. We believe that every child is unique and full of potential. Our warm, nurturing environment is designed to stimulate curiosity, foster creativity, and build a strong foundation of values that lasts a lifetime.")
    intro_image = models.ImageField(upload_to='about/', blank=True, null=True, validators=[validate_image_file])
    
    # Principal's Message
    principal_title = models.CharField(max_length=200, default="Principal's Message")
    principal_name = models.CharField(max_length=150, default="Sr. Mary Teresa, Headmistress")
    principal_message = models.TextField(default="Dear Parents and Well-wishers, Welcome to our joyful family! At St. Mary's, education is not just about textbooks; it is about laughter, discovery, and learning to care for one another. We strive to create a second home where your little ones feel safe, loved, and inspired. Together, let us guide them as they take their first steps towards a bright future.")
    principal_image = models.ImageField(upload_to='about/', blank=True, null=True, validators=[validate_image_file])
    principal_signature = models.CharField(max_length=150, default="Sr. Mary Teresa")
    
    # Parallax Section
    parallax_bg = models.ImageField(upload_to='about/', blank=True, null=True, validators=[validate_image_file])
    parallax_text = models.TextField(default="Educating the mind without educating the heart is no education at all.")

    def __str__(self):
        return "About Us Sections"


class AcademicHighlight(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    # Simple semantic icon names: 'book', 'palette', 'heart', 'sports', 'globe', 'star', 'music'
    icon_class = models.CharField(max_length=50, default="book", help_text="Common names like: book, palette, heart, sports, globe, star, music")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class Achievement(models.Model):
    title = models.CharField(max_length=150)
    value = models.CharField(max_length=50, help_text="e.g. 100%, 25+, 1st Place")
    description = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.value} - {self.title}"


class Facility(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to='facilities/', validators=[validate_image_file])
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Facilities"
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    description = models.TextField()
    cover_image = models.ImageField(upload_to='events/', validators=[validate_image_file])
    is_published = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return self.title


class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='events/additional/', validators=[validate_image_file])
    caption = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Photo for {self.event.title}"


class Announcement(models.Model):
    CATEGORY_CHOICES = [
        ('news', 'News & Updates'),
        ('circular', 'Circulars'),
        ('notice', 'School Notices'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='notice', db_index=True)
    title = models.CharField(max_length=200)
    date = models.DateField()
    description = models.TextField()
    pdf_file = models.FileField(upload_to='announcements/', blank=True, null=True, validators=[validate_pdf_file])
    is_pinned = models.BooleanField(default=False, db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-date', '-created_at']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"


class GalleryAlbum(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='gallery/', validators=[validate_image_file])
    date = models.DateField()
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = "album"
            slug = base_slug
            counter = 1
            while True:
                qs = GalleryAlbum.objects.filter(slug=slug)
                if self.pk:
                    qs = qs.exclude(pk=self.pk)
                if not qs.exists():
                    break
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return self.title


class GalleryPhoto(models.Model):
    album = models.ForeignKey(GalleryAlbum, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='gallery/photos/', validators=[validate_image_file])
    caption = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Photo in {self.album.title}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
