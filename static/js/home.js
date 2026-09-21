// ========== 首页脚本（性能优先） ==========
(function() {
    const reduced = localStorage.getItem('nexus_reduced_motion') === '1';
    if (reduced) document.body.classList.add('nexus-reduced-motion');

    // 星空：小屏/弱动效直接跳过
    const canvas = document.getElementById('starfield');
    if (canvas && canvas.getContext && !reduced) {
        const ctx = canvas.getContext('2d');
        const coarse = matchMedia('(pointer: coarse)').matches;
        const count = coarse ? 28 : 46;
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        let W = 0, H = 0;
        const stars = [];

        function seed() {
            stars.length = 0;
            for (let i = 0; i < count; i++) {
                stars.push({
                    x: Math.random() * W,
                    y: Math.random() * H,
                    r: Math.random() * 1.1 + 0.35,
                    o: Math.random() * 0.45 + 0.25,
                    tw: Math.random() * Math.PI * 2,
                    vx: (Math.random() - 0.5) * 0.05,
                    vy: (Math.random() - 0.5) * 0.05
                });
            }
        }

        function resize() {
            W = window.innerWidth;
            H = window.innerHeight;
            canvas.width = Math.floor(W * dpr);
            canvas.height = Math.floor(H * dpr);
            canvas.style.width = W + 'px';
            canvas.style.height = H + 'px';
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            seed();
        }

        resize();
        addEventListener('resize', resize, { passive: true });

        let raf = 0;
        function draw() {
            ctx.clearRect(0, 0, W, H);
            if (!coarse) {
                const md2 = 110 * 110;
                for (let i = 0; i < stars.length; i++) {
                    for (let j = i + 1; j < stars.length; j++) {
                        const dx = stars[i].x - stars[j].x;
                        const dy = stars[i].y - stars[j].y;
                        const d2 = dx * dx + dy * dy;
                        if (d2 < md2) {
                            ctx.beginPath();
                            ctx.moveTo(stars[i].x, stars[i].y);
                            ctx.lineTo(stars[j].x, stars[j].y);
                            ctx.strokeStyle = 'rgba(130,140,255,' + ((1 - Math.sqrt(d2) / 110) * 0.1) + ')';
                            ctx.lineWidth = 0.55;
                            ctx.stroke();
                        }
                    }
                }
            }
            for (let i = 0; i < stars.length; i++) {
                const s = stars[i];
                s.x += s.vx;
                s.y += s.vy;
                if (s.x < 0) s.x = W;
                if (s.x > W) s.x = 0;
                if (s.y < 0) s.y = H;
                if (s.y > H) s.y = 0;
                s.tw += 0.008;
                const alpha = s.o * (0.55 + 0.45 * Math.sin(s.tw));
                ctx.beginPath();
                ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(200,210,255,' + alpha + ')';
                ctx.fill();
            }
            raf = requestAnimationFrame(draw);
        }
        draw();

        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                cancelAnimationFrame(raf);
            } else {
                raf = requestAnimationFrame(draw);
            }
        });
    }

    // 粒子
    const particles = document.getElementById('particles');
    if (particles && !reduced) {
        const n = matchMedia('(pointer: coarse)').matches ? 3 : 5;
        for (let i = 0; i < n; i++) {
            const p = document.createElement('div');
            p.className = 'particle';
            const sz = Math.random() * 2 + 1;
            p.style.width = sz + 'px';
            p.style.height = sz + 'px';
            p.style.left = Math.random() * 100 + '%';
            p.style.background = 'rgba(150,180,255,' + (Math.random() * 0.14 + 0.06) + ')';
            p.style.animationDuration = (Math.random() * 16 + 16) + 's';
            p.style.animationDelay = (-Math.random() * 14) + 's';
            particles.appendChild(p);
        }
    }

    // 语录
    const quoteEl = document.getElementById('quote');
    const quoteArea = document.getElementById('home-quote-area');
    if (quoteEl) {
        if (localStorage.getItem('nexus_quote_off') === '1') {
            if (quoteArea) quoteArea.style.display = 'none';
        } else {
            const quotes = [
                '今天也要好好写代码呀',
                'Bug 是改不完的，但咖啡可以续杯',
                '能跑就行.jpg',
                '先上线再说，优化是下个季度的事',
                '这个需求很简单，怎么实现我不管',
                '代码和人有一个能跑就行',
                'git push --force，世界清净了',
                '我不是在写 bug，我是在制造就业机会',
            ];
            let idx = Math.floor(Math.random() * quotes.length);
            quoteEl.textContent = quotes[idx];
            quoteEl.style.transition = 'opacity 0.45s ease';
            setInterval(function() {
                quoteEl.style.opacity = '0';
                setTimeout(function() {
                    idx = (idx + 1) % quotes.length;
                    quoteEl.textContent = quotes[idx];
                    quoteEl.style.opacity = '1';
                }, 450);
            }, 6000);
        }
    }
})();
