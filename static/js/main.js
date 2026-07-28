document.addEventListener('DOMContentLoaded', () => {
    // ==========================================
    // NAVBAR & MOBILE MENU
    // ==========================================
    const navbar = document.querySelector('.navbar');
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Scrolled Navbar Effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Toggle Mobile Menu
    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active'); // State indicator for button
            
            // Hamburger Animation
            const spans = navToggle.querySelectorAll('span');
            spans[0].style.transform = navMenu.classList.contains('active') ? 'rotate(45deg) translate(6px, 6px)' : 'none';
            spans[1].style.opacity = navMenu.classList.contains('active') ? '0' : '1';
            spans[2].style.transform = navMenu.classList.contains('active') ? 'rotate(-45deg) translate(6px, -6px)' : 'none';
        });
    }
    
    // Close Mobile Menu on Link Click
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
            navToggle.classList.remove('active'); // Close state indicator
            const spans = navToggle.querySelectorAll('span');
            spans.forEach(span => span.removeAttribute('style'));
        });
    });

    // ==========================================
    // SCROLL SPY (Active Nav Highlights)
    // ==========================================
    const sections = document.querySelectorAll('section, header');
    const observerOptions = {
        root: null,
        rootMargin: '-40% 0px -40% 0px', // check center of viewport
        threshold: 0
    };
    
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                navLinks.forEach(link => {
                    if (link.getAttribute('href') === `#${id}`) {
                        link.classList.add('active');
                    } else {
                        link.classList.remove('active');
                    }
                });
            }
        });
    }, observerOptions);
    
    sections.forEach(section => {
        if (section.getAttribute('id')) {
            sectionObserver.observe(section);
        }
    });


    // ==========================================
    // GALLERY & EVENT LIGHTBOX (No Library)
    // ==========================================
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = lightbox ? lightbox.querySelector('.lightbox-img') : null;
    const lightboxCaption = lightbox ? lightbox.querySelector('.lightbox-caption') : null;
    const lightboxClose = lightbox ? lightbox.querySelector('.lightbox-close') : null;
    const lightboxPrev = lightbox ? lightbox.querySelector('.lightbox-prev') : null;
    const lightboxNext = lightbox ? lightbox.querySelector('.lightbox-next') : null;
    const lightboxThumbContainer = lightbox ? lightbox.querySelector('.lightbox-thumbnails') : null;
    
    let currentAlbumPhotos = [];
    let currentPhotoIndex = 0;
    
    // Function to open Lightbox
    const openLightbox = (photos, startIndex = 0) => {
        if (!lightbox) return;
        currentAlbumPhotos = photos;
        currentPhotoIndex = startIndex;
        
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden'; // stop page scrolling
        
        renderLightboxPhoto();
        renderLightboxThumbnails();
    };
    
    // Render Lightbox Photo Details
    const renderLightboxPhoto = () => {
        if (!lightboxImg || currentAlbumPhotos.length === 0) return;
        const photo = currentAlbumPhotos[currentPhotoIndex];
        
        // Soft fade transition
        lightboxImg.style.opacity = 0;
        setTimeout(() => {
            lightboxImg.src = photo.url;
            lightboxImg.alt = photo.caption || 'School Photo';
            lightboxCaption.textContent = photo.caption || '';
            lightboxImg.style.opacity = 1;
        }, 150);
    };
    
    // Render Navigation Thumbnails in Lightbox
    const renderLightboxThumbnails = () => {
        if (!lightboxThumbContainer) return;
        lightboxThumbContainer.innerHTML = '';
        
        // Hide thumbnail strip if only 1 image
        if (currentAlbumPhotos.length <= 1) {
            lightboxThumbContainer.style.display = 'none';
            return;
        }
        lightboxThumbContainer.style.display = 'flex';
        
        currentAlbumPhotos.forEach((photo, idx) => {
            const thumb = document.createElement('img');
            thumb.src = photo.url;
            thumb.className = `lightbox-thumb ${idx === currentPhotoIndex ? 'active' : ''}`;
            thumb.alt = 'Thumbnail';
            thumb.addEventListener('click', () => {
                currentPhotoIndex = idx;
                renderLightboxPhoto();
                // Update active class
                document.querySelectorAll('.lightbox-thumb').forEach((t, i) => {
                    t.classList.toggle('active', i === idx);
                });
            });
            lightboxThumbContainer.appendChild(thumb);
        });
    };
    
    // Slide Controls
    const prevSlide = () => {
        if (currentAlbumPhotos.length <= 1) return;
        currentPhotoIndex = (currentPhotoIndex - 1 + currentAlbumPhotos.length) % currentAlbumPhotos.length;
        renderLightboxPhoto();
        updateActiveThumbnail();
    };
    
    const nextSlide = () => {
        if (currentAlbumPhotos.length <= 1) return;
        currentPhotoIndex = (currentPhotoIndex + 1) % currentAlbumPhotos.length;
        renderLightboxPhoto();
        updateActiveThumbnail();
    };
    
    const updateActiveThumbnail = () => {
        const thumbs = document.querySelectorAll('.lightbox-thumb');
        thumbs.forEach((t, i) => {
            t.classList.toggle('active', i === currentPhotoIndex);
        });
        // Scroll active thumbnail into view
        const activeThumb = thumbs[currentPhotoIndex];
        if (activeThumb && lightboxThumbContainer) {
            lightboxThumbContainer.scrollTo({
                left: activeThumb.offsetLeft - (lightboxThumbContainer.offsetWidth / 2) + (activeThumb.offsetWidth / 2),
                behavior: 'smooth'
            });
        }
    };
    
    // Close Lightbox
    const closeLightbox = () => {
        if (!lightbox) return;
        lightbox.classList.remove('active');
        document.body.style.overflow = ''; // restore scrolling
    };
    
    // Attach Listeners to Lightbox Controls
    if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
    if (lightboxPrev) lightboxPrev.addEventListener('click', prevSlide);
    if (lightboxNext) lightboxNext.addEventListener('click', nextSlide);
    
    // Close on overlay background click
    if (lightbox) {
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox || e.target.classList.contains('lightbox-container') || e.target.classList.contains('lightbox-content')) {
                closeLightbox();
            }
        });
    }
    
    // Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {
        if (!lightbox || !lightbox.classList.contains('active')) return;
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft') prevSlide();
        if (e.key === 'ArrowRight') nextSlide();
    });
    
    // Bind public album clicks
    const albumCards = document.querySelectorAll('.album-card');
    albumCards.forEach(card => {
        card.addEventListener('click', () => {
            const rawData = card.getAttribute('data-photos');
            if (rawData) {
                try {
                    const photos = JSON.parse(rawData);
                    if (photos && photos.length > 0) {
                        openLightbox(photos);
                    }
                } catch (e) {
                    console.error('Error parsing album photos data', e);
                }
            }
        });
    });
    
    // Bind event additional photo triggers
    const eventTriggers = document.querySelectorAll('.event-gallery-trigger');
    eventTriggers.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            const rawData = trigger.getAttribute('data-photos');
            if (rawData) {
                try {
                    const photos = JSON.parse(rawData);
                    if (photos && photos.length > 0) {
                        openLightbox(photos);
                    }
                } catch (e) {
                    console.error('Error parsing event photos data', e);
                }
            }
        });
    });

    // ==========================================
    // AJAX CONTACT FORM SUBMISSION
    // ==========================================
    const contactForm = document.getElementById('contactForm');
    const formFeedback = document.getElementById('formFeedback');
    
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // Show loading state
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Sending... <i class="fas fa-spinner fa-spin"></i>';
            
            // Clean previous validation feedback
            formFeedback.className = 'form-feedback';
            formFeedback.style.display = 'none';
            document.querySelectorAll('.form-field').forEach(field => {
                field.style.borderColor = '';
            });
            
            // Gather post fields
            const formData = new FormData(contactForm);
            
            fetch(contactForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
                
                if (data.success) {
                    // Success Message
                    formFeedback.classList.add('success');
                    formFeedback.textContent = data.message;
                    formFeedback.style.display = 'block';
                    
                    contactForm.reset();
                    
                    // Auto-scroll slightly to feedback
                    formFeedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                } else {
                    // Validation Errors
                    formFeedback.classList.add('error');
                    formFeedback.textContent = 'Oops! Please correct the errors in the fields highlighted below.';
                    formFeedback.style.display = 'block';
                    
                    // Highlight specific error fields
                    Object.keys(data.errors).forEach(key => {
                        const field = contactForm.querySelector(`[name="${key}"]`);
                        if (field) {
                            field.style.borderColor = 'var(--color-secondary)';
                        }
                    });
                }
            })
            .catch(err => {
                console.error('Error submitting form', err);
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
                
                formFeedback.classList.add('error');
                formFeedback.textContent = 'A connection error occurred. Please try again later.';
                formFeedback.style.display = 'block';
            });
        });
    }
});
