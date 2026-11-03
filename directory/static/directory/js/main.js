/* ==========================================================================
   VentureVault - Interactive JavaScript System
   Handles AJAX video bookmarking, link sharing, and dynamic notifications
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    // 1. CSRF Helper for Django AJAX
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // 2. Global Saved Count Updater
    function updateGlobalSavedBadge(count) {
        let badge = document.getElementById('nav-saved-count');
        if (count > 0) {
            if (!badge) {
                const profileBtn = document.querySelector('.nav-profile-btn');
                if (profileBtn) {
                    badge = document.createElement('span');
                    badge.id = 'nav-saved-count';
                    badge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-warning text-dark fw-bold';
                    profileBtn.appendChild(badge);
                }
            }
            if (badge) {
                badge.textContent = count;
                badge.style.display = 'inline-block';
            }
        } else if (badge) {
            badge.style.display = 'none';
        }
    }

    // 3. Detail Page Toggle Save Video Button
    const saveDetailBtn = document.getElementById('btn-save-video');
    if (saveDetailBtn) {
        saveDetailBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const videoId = this.getAttribute('data-video-id');
            if (!videoId) return;

            fetch(`/video/${videoId}/toggle-save/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({})
            })
            .then(res => {
                if (res.status === 401) {
                    return res.json().then(data => {
                        window.location.href = data.login_url || '/login/';
                    });
                }
                if (res.status === 403) {
                    return res.json().then(data => {
                        showToast(data.message || 'Admins cannot bookmark stories.', 'error');
                    });
                }
                return res.json();
            })
            .then(data => {
                if (data && data.status === 'success') {
                    const icon = saveDetailBtn.querySelector('i');
                    const textSpan = saveDetailBtn.querySelector('.save-btn-text');

                    if (data.is_saved) {
                        saveDetailBtn.classList.remove('btn-vv-outline');
                        saveDetailBtn.classList.add('btn-vv-primary');
                        if (icon) icon.className = 'fas fa-bookmark me-1';
                        if (textSpan) textSpan.textContent = 'Saved in Vault';
                    } else {
                        saveDetailBtn.classList.remove('btn-vv-primary');
                        saveDetailBtn.classList.add('btn-vv-outline');
                        if (icon) icon.className = 'far fa-bookmark me-1';
                        if (textSpan) textSpan.textContent = 'Save to Vault';
                    }

                    updateGlobalSavedBadge(data.saved_count);
                    showToast(data.message, 'success');
                }
            })
            .catch(err => {
                console.error('Error toggling saved video:', err);
                showToast("Could not update saved status. Please try again.", 'error');
            });
        });
    }

    // 4. Card-level Quick Save Buttons (.btn-card-save)
    document.querySelectorAll('.btn-card-save').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const videoId = this.getAttribute('data-video-id');
            if (!videoId) return;

            fetch(`/video/${videoId}/toggle-save/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({})
            })
            .then(res => {
                if (res.status === 401) {
                    return res.json().then(data => {
                        window.location.href = data.login_url || '/login/';
                    });
                }
                if (res.status === 403) {
                    return res.json().then(data => {
                        showToast(data.message || 'Admins cannot bookmark stories.', 'error');
                    });
                }
                return res.json();
            })
            .then(data => {
                if (data && data.status === 'success') {
                    const icon = btn.querySelector('i');
                    if (data.is_saved) {
                        btn.classList.add('saved');
                        if (icon) icon.className = 'fas fa-bookmark';
                        btn.setAttribute('title', 'Remove from Vault');
                    } else {
                        btn.classList.remove('saved');
                        if (icon) icon.className = 'far fa-bookmark';
                        btn.setAttribute('title', 'Save to Vault');
                    }
                    updateGlobalSavedBadge(data.saved_count);
                    showToast(data.message, 'success');
                }
            })
            .catch(err => {
                console.error('Error toggling save on card:', err);
            });
        });
    });

    // 5. Share Button: Copy link to clipboard
    const shareBtn = document.getElementById('btn-share-video');
    if (shareBtn) {
        shareBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (navigator.clipboard && window.location.href) {
                navigator.clipboard.writeText(window.location.href).then(() => {
                    showToast("Video link copied to clipboard!", "success");
                }).catch(() => {
                    fallbackCopyText(window.location.href);
                });
            } else {
                fallbackCopyText(window.location.href);
            }
        });
    }

    function fallbackCopyText(text) {
        const dummy = document.createElement("input");
        document.body.appendChild(dummy);
        dummy.value = text;
        dummy.select();
        document.execCommand("copy");
        document.body.removeChild(dummy);
        showToast("Video link copied to clipboard!", "success");
    }

    // 6. Toast Notification Builder
    function showToast(msg, type) {
        let toastContainer = document.getElementById('vv-toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'vv-toast-container';
            toastContainer.style.position = 'fixed';
            toastContainer.style.bottom = '24px';
            toastContainer.style.right = '24px';
            toastContainer.style.zIndex = '9999';
            toastContainer.style.display = 'flex';
            toastContainer.style.flexDirection = 'column';
            toastContainer.style.gap = '8px';
            document.body.appendChild(toastContainer);
        }

        const iconClass = type === 'error' ? 'fa-exclamation-circle text-danger' : 'fa-check-circle text-warning';

        const toast = document.createElement('div');
        toast.className = 'shadow-lg border';
        toast.style.backgroundColor = '#14213D';
        toast.style.color = '#FFFFFF';
        toast.style.borderRadius = '8px';
        toast.style.padding = '12px 16px';
        toast.style.fontSize = '0.9rem';
        toast.style.display = 'flex';
        toast.style.alignItems = 'center';
        toast.style.gap = '10px';
        toast.style.borderLeft = '4px solid #FCA311';
        toast.style.boxShadow = '0 10px 25px rgba(20, 33, 61, 0.4)';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.25s ease';

        toast.innerHTML = `
            <i class="fas ${iconClass} fs-5"></i>
            <span style="font-weight: 500;">${msg}</span>
        `;

        toastContainer.appendChild(toast);

        // Animate entrance
        requestAnimationFrame(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        });

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            setTimeout(() => toast.remove(), 250);
        }, 3200);
    }
});
