// ========== 星空+星座 ==========
(function() {
    const c = document.getElementById('starfield'), ctx = c.getContext('2d');
    let W, H;
    function resize() { W = c.width = innerWidth; H = c.height = innerHeight; stars.forEach(s => { s.x = Math.random()*W; s.y = Math.random()*H; }); }
    const stars = Array.from({length: 50}, () => ({
        x: Math.random()*2000, y: Math.random()*2000,
        r: Math.random()*1.3+0.4, o: Math.random()*0.5+0.3,
        tw: Math.random()*Math.PI*2,
        vx: (Math.random()-0.5)*0.08, vy: (Math.random()-0.5)*0.08
    }));
    resize(); addEventListener('resize', resize);
    function draw() {
        ctx.clearRect(0,0,W,H);
        const md2 = 120*120;
        for (let i=0;i<stars.length;i++) for (let j=i+1;j<stars.length;j++) {
            const dx=stars[i].x-stars[j].x, dy=stars[i].y-stars[j].y, d2=dx*dx+dy*dy;
            if (d2<md2) { ctx.beginPath(); ctx.moveTo(stars[i].x,stars[i].y); ctx.lineTo(stars[j].x,stars[j].y); ctx.strokeStyle=`rgba(130,140,255,${(1-Math.sqrt(d2)/180)*0.12})`; ctx.lineWidth=0.6; ctx.stroke(); }
        }
        stars.forEach(s => {
            s.x+=s.vx; s.y+=s.vy;
            if(s.x<0)s.x=W; if(s.x>W)s.x=0; if(s.y<0)s.y=H; if(s.y>H)s.y=0;
            s.tw+=0.01;
            ctx.beginPath(); ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
            ctx.fillStyle=`rgba(200,210,255,${s.o*(0.5+0.5*Math.sin(s.tw))})`; ctx.fill();
        });
        requestAnimationFrame(draw);
    }
    draw();
})();

// ========== 粒子 ==========
(function() {
    const c = document.getElementById('particles');
    for (let i=0;i<6;i++) { const p=document.createElement('div'); p.className='particle'; const sz=Math.random()*2.5+1; p.style.cssText=`width:${sz}px;height:${sz}px;left:${Math.random()*100}%;background:rgba(150,180,255,${Math.random()*0.18+0.08});animation-duration:${Math.random()*18+14}s;animation-delay:-${Math.random()*14}s;`; c.appendChild(p); }
})();

// ========== 鼠标光球 ==========
(function() {
    const s = document.getElementById('spotlight');
    let mx=0,my=0,sx=0,sy=0;
    addEventListener('mousemove', e => { mx=e.clientX; my=e.clientY; });
    (function r() { sx+=(mx-sx)*0.35; sy+=(my-sy)*0.35; s.style.transform=`translate(${sx-190}px,${sy-190}px)`; requestAnimationFrame(r); })();
})();

// ========== 语录轮换 ==========
(function() {
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
    const el = document.getElementById('quote');
    if (!el) return;
    let idx = Math.floor(Math.random() * quotes.length);
    el.textContent = quotes[idx];
    el.style.transition = 'opacity 0.5s ease';
    setInterval(() => {
        el.style.opacity = '0';
        setTimeout(() => {
            idx = (idx + 1) % quotes.length;
            el.textContent = quotes[idx];
            el.style.opacity = '1';
        }, 500);
    }, 5000);
})();

// ========== 时钟 ==========
(function() {
    const el=document.getElementById('clock'), d=document.getElementById('clock-date');
    const el2=document.getElementById('clock-mobile'), d2=document.getElementById('clock-date-mobile');
    const w=['日','一','二','三','四','五','六'];
    function t() {
        const n=new Date();
        const time=String(n.getHours()).padStart(2,'0')+':'+String(n.getMinutes()).padStart(2,'0')+':'+String(n.getSeconds()).padStart(2,'0');
        const date=(n.getMonth()+1)+'/'+n.getDate()+' 周'+w[n.getDay()];
        el.textContent=time; d.textContent=date;
        if(el2){ el2.textContent=time; d2.textContent=date; }
    }
    t(); setInterval(t,1000);
})();


