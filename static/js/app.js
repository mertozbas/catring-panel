// Başak Yemek - Ortak JS

document.addEventListener('DOMContentLoaded', function() {
    // PWA: Service Worker kaydi
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').catch(function(err) {
            console.log('SW kayit hatasi:', err);
        });
    }

    const dateEl = document.getElementById('current-date');
    if (dateEl) {
        const now = new Date();
        const days = ['Pazar', 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi'];
        const months = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                        'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
        dateEl.textContent = `${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}, ${days[now.getDay()]}`;
    }

    // Auto-dismiss alerts after 5s
    document.querySelectorAll('.alert').forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() { alert.remove(); }, 300);
        }, 5000);
    });

    // Mobile: sidebar linkine tiklayinca kapansin
    document.querySelectorAll('.sidebar-menu a').forEach(function(link) {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                var sidebar = document.getElementById('sidebar');
                var backdrop = document.getElementById('sidebarBackdrop');
                sidebar.classList.remove('open');
                if (backdrop) backdrop.classList.remove('active');
            }
        });
    });

    // Modal overlay tiklayinca kapansin
    document.querySelectorAll('.modal-overlay').forEach(function(overlay) {
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                overlay.classList.remove('active');
            }
        });
    });
});

function toggleSidebar() {
    var sidebar = document.getElementById('sidebar');
    var backdrop = document.getElementById('sidebarBackdrop');
    sidebar.classList.toggle('open');
    if (backdrop) {
        backdrop.classList.toggle('active', sidebar.classList.contains('open'));
    }
}

function openModal(id) {
    document.getElementById(id).classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

function confirmDelete(msg) {
    return confirm(msg || 'Bu kaydı silmek istediğinize emin misiniz?');
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('tr-TR');
}

function getToday() {
    return new Date().toISOString().split('T')[0];
}

function getContainerLabel(type) {
    const labels = {
        'sefer_tasi': 'Sefer Tası',
        'paket': 'Paket',
        'kuvet': 'Küvet',
        'tepsi': 'Tepsi',
        'poset': 'Poşet'
    };
    return labels[type] || type;
}

function getCategoryLabel(cat) {
    const labels = {
        'corba': 'Çorba',
        'ana_yemek': 'Ana Yemek',
        'garnitur': 'Garnitür',
        'tatli': 'Tatlı',
        'icecek': 'İçecek'
    };
    return labels[cat] || cat;
}

function getDayName(dayNum) {
    const days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi'];
    return days[dayNum] || '';
}
