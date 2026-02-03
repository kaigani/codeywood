/**
 * Production Bible - Interactions
 * Lightbox, gallery, sidebar, collapsibles
 */

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initLightbox();
    initCollapsibles();
    initActiveNav();
});

/* ---- Sidebar Toggle (Mobile) ---- */

function initSidebar() {
    const toggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.bible-sidebar');
    if (!toggle || !sidebar) return;

    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        toggle.textContent = sidebar.classList.contains('open') ? 'CLOSE' : 'MENU';
    });

    // Close sidebar when clicking a link (mobile)
    sidebar.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 860) {
                sidebar.classList.remove('open');
                toggle.textContent = 'MENU';
            }
        });
    });
}

/* ---- Lightbox Gallery ---- */

function initLightbox() {
    const galleryItems = document.querySelectorAll('.gallery-item[data-lightbox]');
    if (galleryItems.length === 0) return;

    // Create lightbox element
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <div class="lightbox-content">
            <button class="lightbox-close">[X] CLOSE</button>
            <button class="lightbox-nav lightbox-prev">&#9664;</button>
            <button class="lightbox-nav lightbox-next">&#9654;</button>
            <img src="" alt="">
            <div class="lightbox-caption"></div>
        </div>
    `;
    document.body.appendChild(lightbox);

    const lbImg = lightbox.querySelector('img');
    const lbCaption = lightbox.querySelector('.lightbox-caption');
    const lbClose = lightbox.querySelector('.lightbox-close');
    const lbPrev = lightbox.querySelector('.lightbox-prev');
    const lbNext = lightbox.querySelector('.lightbox-next');

    let currentGroup = [];
    let currentIndex = 0;

    function openLightbox(item) {
        const group = item.dataset.lightbox || 'default';
        currentGroup = Array.from(
            document.querySelectorAll(`.gallery-item[data-lightbox="${group}"]`)
        );
        currentIndex = currentGroup.indexOf(item);
        showImage(currentIndex);
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function showImage(index) {
        const item = currentGroup[index];
        const img = item.querySelector('img');
        const label = item.querySelector('.gallery-item-label');
        lbImg.src = img.src;
        lbImg.alt = img.alt;
        lbCaption.textContent = label ? label.textContent : img.alt;

        lbPrev.style.display = index > 0 ? 'flex' : 'none';
        lbNext.style.display = index < currentGroup.length - 1 ? 'flex' : 'none';
    }

    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }

    galleryItems.forEach(item => {
        item.addEventListener('click', () => openLightbox(item));
    });

    lbClose.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) closeLightbox();
    });

    lbPrev.addEventListener('click', (e) => {
        e.stopPropagation();
        if (currentIndex > 0) {
            currentIndex--;
            showImage(currentIndex);
        }
    });

    lbNext.addEventListener('click', (e) => {
        e.stopPropagation();
        if (currentIndex < currentGroup.length - 1) {
            currentIndex++;
            showImage(currentIndex);
        }
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (!lightbox.classList.contains('active')) return;
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft' && currentIndex > 0) {
            currentIndex--;
            showImage(currentIndex);
        }
        if (e.key === 'ArrowRight' && currentIndex < currentGroup.length - 1) {
            currentIndex++;
            showImage(currentIndex);
        }
    });
}

/* ---- Collapsible Sections ---- */

function initCollapsibles() {
    document.querySelectorAll('[data-collapsible]').forEach(trigger => {
        const targetId = trigger.dataset.collapsible;
        const target = document.getElementById(targetId);
        if (!target) return;

        // Set initial state
        if (!trigger.classList.contains('open')) {
            target.style.display = 'none';
        }

        trigger.addEventListener('click', () => {
            const isOpen = trigger.classList.toggle('open');
            target.style.display = isOpen ? '' : 'none';

            // Update arrow indicator
            const arrow = trigger.querySelector('.collapse-arrow');
            if (arrow) {
                arrow.textContent = isOpen ? '[-]' : '[+]';
            }
        });
    });
}

/* ---- Active Nav Highlight ---- */

function initActiveNav() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-section a').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage) {
            link.classList.add('active');
        }
    });
}
