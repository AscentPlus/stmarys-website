document.addEventListener('DOMContentLoaded', () => {
    // ==========================================
    // MOBILE SIDEBAR TOGGLE
    // ==========================================
    const sidebar = document.getElementById('cmsSidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarClose = document.getElementById('sidebarClose');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking close button
        if (sidebarClose) {
            sidebarClose.addEventListener('click', () => {
                sidebar.classList.remove('active');
            });
        }
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (sidebar.classList.contains('active') && !sidebar.contains(e.target) && e.target !== sidebarToggle && e.target !== sidebarClose) {
                sidebar.classList.remove('active');
            }
        });
    }

    // ==========================================
    // CMS TAB SWITCHING
    // ==========================================
    const tabs = document.querySelectorAll('.cms-tab');
    const tabContents = document.querySelectorAll('.cms-tab-content');
    
    if (tabs.length > 0) {
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.getAttribute('data-tab');
                
                // Toggle active class on tab buttons
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Toggle active class on contents
                tabContents.forEach(content => {
                    if (content.id === target) {
                        content.classList.add('active');
                    } else {
                        content.classList.remove('active');
                    }
                });
                
                // Save active tab in local storage to keep state on refresh
                localStorage.setItem('activeCmsTab', target);
            });
        });
        
        // Restore tab on reload
        const savedTab = localStorage.getItem('activeCmsTab');
        if (savedTab) {
            const tabBtn = document.querySelector(`.cms-tab[data-tab="${savedTab}"]`);
            if (tabBtn) {
                tabBtn.click();
            }
        }
    }

    // ==========================================
    // MODAL WINDOW HANDLING (Add & Edit)
    // ==========================================
    const modals = document.querySelectorAll('.cms-modal');
    const modalCloseButtons = document.querySelectorAll('.cms-modal-close, .modal-cancel');
    
    // Close Modals
    const closeAllModals = () => {
        modals.forEach(m => m.classList.remove('active'));
        document.body.style.overflow = '';
    };
    
    modalCloseButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            closeAllModals();
        });
    });
    
    // Close modal on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeAllModals();
    });
    
    // Close modal on clicking overlay bg
    modals.forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeAllModals();
        });
    });

    // Open Modal Helper
    window.openCmsModal = (modalId) => {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    };

    // ==========================================
    // ABOUT US SUB-ITEM ACTIONS
    // ==========================================
    
    // 1. Academic Highlights Modals
    const highlightModal = document.getElementById('highlightModal');
    const highlightForm = highlightModal ? highlightModal.querySelector('form') : null;
    const addHighlightBtn = document.getElementById('addHighlightBtn');
    const editHighlightBtns = document.querySelectorAll('.edit-highlight-btn');
    
    if (addHighlightBtn && highlightForm) {
        addHighlightBtn.addEventListener('click', () => {
            // Reset form details for Add mode
            highlightForm.reset();
            highlightForm.action = addHighlightBtn.getAttribute('data-action-url');
            highlightModal.querySelector('.cms-modal-header h3').textContent = 'Add Academic Highlight';
            openCmsModal('highlightModal');
        });
    }
    
    editHighlightBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (!highlightForm) return;
            // Load values from dataset attributes
            highlightForm.action = btn.getAttribute('data-action-url');
            highlightForm.querySelector('[name="title"]').value = btn.dataset.title;
            highlightForm.querySelector('[name="description"]').value = btn.dataset.description;
            highlightForm.querySelector('[name="icon_class"]').value = btn.dataset.icon;
            highlightForm.querySelector('[name="order"]').value = btn.dataset.order;
            
            highlightModal.querySelector('.cms-modal-header h3').textContent = 'Edit Academic Highlight';
            openCmsModal('highlightModal');
        });
    });

    // 2. Achievements Modals
    const achievementModal = document.getElementById('achievementModal');
    const achievementForm = achievementModal ? achievementModal.querySelector('form') : null;
    const addAchievementBtn = document.getElementById('addAchievementBtn');
    const editAchievementBtns = document.querySelectorAll('.edit-achievement-btn');
    
    if (addAchievementBtn && achievementForm) {
        addAchievementBtn.addEventListener('click', () => {
            achievementForm.reset();
            achievementForm.action = addAchievementBtn.getAttribute('data-action-url');
            achievementModal.querySelector('.cms-modal-header h3').textContent = 'Add Achievement';
            openCmsModal('achievementModal');
        });
    }
    
    editAchievementBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (!achievementForm) return;
            achievementForm.action = btn.getAttribute('data-action-url');
            achievementForm.querySelector('[name="title"]').value = btn.dataset.title;
            achievementForm.querySelector('[name="value"]').value = btn.dataset.value;
            achievementForm.querySelector('[name="description"]').value = btn.dataset.description;
            achievementForm.querySelector('[name="order"]').value = btn.dataset.order;
            
            achievementModal.querySelector('.cms-modal-header h3').textContent = 'Edit Achievement';
            openCmsModal('achievementModal');
        });
    });

    // 3. Facilities Modals
    const facilityModal = document.getElementById('facilityModal');
    const facilityForm = facilityModal ? facilityModal.querySelector('form') : null;
    const addFacilityBtn = document.getElementById('addFacilityBtn');
    const editFacilityBtns = document.querySelectorAll('.edit-facility-btn');
    
    if (addFacilityBtn && facilityForm) {
        addFacilityBtn.addEventListener('click', () => {
            facilityForm.reset();
            facilityForm.action = addFacilityBtn.getAttribute('data-action-url');
            // Remove required image flag for edit, but add for add
            const imgInput = facilityForm.querySelector('[name="image"]');
            if (imgInput) imgInput.setAttribute('required', 'required');
            facilityModal.querySelector('.cms-modal-header h3').textContent = 'Add Facility';
            openCmsModal('facilityModal');
        });
    }
    
    editFacilityBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (!facilityForm) return;
            facilityForm.action = btn.getAttribute('data-action-url');
            facilityForm.querySelector('[name="title"]').value = btn.dataset.title;
            facilityForm.querySelector('[name="description"]').value = btn.dataset.description;
            facilityForm.querySelector('[name="order"]').value = btn.dataset.order;
            
            // Image is not strictly required when editing
            const imgInput = facilityForm.querySelector('[name="image"]');
            if (imgInput) imgInput.removeAttribute('required');
            
            facilityModal.querySelector('.cms-modal-header h3').textContent = 'Edit Facility';
            openCmsModal('facilityModal');
        });
    });

    // ==========================================
    // GLOBAL CONFIRMATION MODAL
    // ==========================================
    const confirmModal = document.getElementById('cmsConfirmModal');
    const confirmMessage = document.getElementById('cmsConfirmMessage');
    const confirmConfirmBtn = document.getElementById('cmsConfirmConfirmBtn');
    const confirmCancelBtn = document.getElementById('cmsConfirmCancelBtn');

    window.showCmsConfirm = (message, action) => {
        if (!confirmModal || !confirmMessage || !confirmConfirmBtn) return;
        
        confirmMessage.textContent = message;
        
        if (typeof action === 'string') {
            confirmConfirmBtn.href = action;
            confirmConfirmBtn.onclick = null;
        } else if (typeof action === 'function') {
            confirmConfirmBtn.href = '#';
            confirmConfirmBtn.onclick = (e) => {
                e.preventDefault();
                action();
                closeAllModals();
            };
        }
        
        confirmModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    };

    if (confirmCancelBtn) {
        confirmCancelBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeAllModals();
        });
    }

    // Intercept clicks on links/buttons requesting confirmation
    document.addEventListener('click', (e) => {
        const trigger = e.target.closest('[data-confirm]');
        if (trigger) {
            e.preventDefault();
            const message = trigger.getAttribute('data-confirm');
            const actionUrl = trigger.getAttribute('href');
            
            if (actionUrl && actionUrl !== '#') {
                showCmsConfirm(message, actionUrl);
            } else {
                const form = trigger.closest('form');
                if (form) {
                    showCmsConfirm(message, () => form.submit());
                }
            }
        }
    });
});
