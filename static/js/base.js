// ========== 导航栏：滚动隐藏 + 透明变色 ==========
(function() {
    const nav = document.getElementById('navbar');
    const mobileTopbar = document.getElementById('mobile-topbar');
    let lastScroll = 0;
    let ticking = false;
    const threshold = 80;

    function updateNav() {
        const scrollY = window.scrollY;
        // 桌面端导航栏
        if (nav) {
            if (scrollY > 20) {
                nav.classList.remove('nav-transparent');
                nav.classList.add('nav-solid');
            } else {
                nav.classList.remove('nav-solid');
                nav.classList.add('nav-transparent');
            }
            if (scrollY > threshold) {
                if (scrollY > lastScroll + 8) {
                    nav.classList.add('nav-hidden');
                } else if (scrollY < lastScroll - 3) {
                    nav.classList.remove('nav-hidden');
                }
            } else {
                nav.classList.remove('nav-hidden');
            }
        }
        // 移动端顶部栏背景
        if (mobileTopbar) {
            if (scrollY > 20) {
                mobileTopbar.style.background = 'rgba(6, 6, 14, 0.85)';
            } else {
                mobileTopbar.style.background = 'transparent';
            }
        }
        lastScroll = scrollY;
        ticking = false;
    }

    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(() => updateNav());
            ticking = true;
        }
    }, { passive: true });
    updateNav();
})();

// ========== 回到顶部按钮 ==========
(function() {
    const btn = document.getElementById('back-to-top');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            btn.classList.add('visible');
        } else {
            btn.classList.remove('visible');
        }
    }, { passive: true });
})();

// ========== 移动端菜单（已改为底部Tab栏） ==========


// ========== 时钟 ==========
(function() {
    const clock = document.getElementById('nav-clock');
    const clockMobile = document.getElementById('nav-clock-mobile');
    function updateClock() {
        const now = new Date();
        const h = String(now.getHours()).padStart(2, '0');
        const m = String(now.getMinutes()).padStart(2, '0');
        const text = h + ':' + m;
        if (clock) clock.textContent = text;
        if (clockMobile) clockMobile.textContent = text;
    }
    updateClock();
    setInterval(updateClock, 30000);
})();

// ========== 快捷键 ==========
document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) return;

    if (e.key === '/') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.focus();
        } else {
            window.location.href = '/blog/';
        }
    }

    if (e.key === 'e' || e.key === 'E') {
        e.preventDefault();
        togglePin();
    }

    if (e.key === 'Escape') {
        closePinModal();
    }
});

// ========== PIN 输入框逻辑 ==========
const pinBoxes = document.querySelectorAll('.pin-box');

pinBoxes.forEach((box, index) => {
    box.addEventListener('input', (e) => {
        const value = e.target.value;
        if (!/^\d$/.test(value)) {
            e.target.value = '';
            return;
        }
        box.classList.add('filled');
        if (value && index < 5) {
            pinBoxes[index + 1].focus();
        }
        if (index === 5 && value) {
            setTimeout(verifyPin, 100);
        }
    });

    box.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace' && !e.target.value && index > 0) {
            pinBoxes[index - 1].focus();
            pinBoxes[index - 1].value = '';
            pinBoxes[index - 1].classList.remove('filled');
        }
    });

    box.addEventListener('focus', () => {
        box.select();
    });
});

function togglePin() {
    // 已解锁状态 → 直接锁定
    if (document.body.classList.contains('pin-unlocked')) {
        fetch('/api/lock-pin/', { method: 'POST' }).then(() => location.reload());
        return;
    }
    // 未解锁 → 弹密码框
    const modal = document.getElementById('pin-modal');
    if (modal.classList.contains('hidden')) {
        modal.classList.remove('hidden');
        pinBoxes[0].focus();
    } else {
        closePinModal();
    }
}

function closePinModal() {
    document.getElementById('pin-modal').classList.add('hidden');
    pinBoxes.forEach(box => {
        box.value = '';
        box.classList.remove('filled', 'error');
    });
    document.getElementById('pin-error').classList.add('hidden');
}

function getPin() {
    let pin = '';
    pinBoxes.forEach(box => pin += box.value);
    return pin;
}

function showError() {
    document.getElementById('pin-error').classList.remove('hidden');
    pinBoxes.forEach(box => {
        box.value = '';
        box.classList.remove('filled');
        box.classList.add('error');
    });
    setTimeout(() => {
        pinBoxes.forEach(box => box.classList.remove('error'));
        pinBoxes[0].focus();
    }, 500);
}

function verifyPin() {
    const pin = getPin();
    if (pin.length !== 6) return;

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
        || document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1]
        || '';

    fetch('/api/verify-pin/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({pin: pin})
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            const btn = document.getElementById('pin-toggle');
            btn.textContent = '🔓';
            const pinMobile = document.getElementById('pin-toggle-mobile');
            if (pinMobile) pinMobile.textContent = '🔓';
            document.body.classList.add('pin-unlocked');
            closePinModal();
            location.reload();
        } else {
            showError();
        }
    })
    .catch(() => {
        showError();
    });
}
