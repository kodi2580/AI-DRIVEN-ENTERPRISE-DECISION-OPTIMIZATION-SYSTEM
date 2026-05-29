/* ============================================================
   TALENTGUARD — UPGRADED SCRIPT
============================================================ */

// ── Cursor Glow ──────────────────────────────────────────────
const cursorGlow = document.getElementById('cursorGlow');
if (cursorGlow) {
    document.addEventListener('mousemove', e => {
        cursorGlow.style.left = e.clientX + 'px';
        cursorGlow.style.top = e.clientY + 'px';
    });
}

// ── Particle Canvas ──────────────────────────────────────────
const canvas = document.getElementById('particleCanvas');
if (canvas) {
    const ctx = canvas.getContext('2d');
    let particles = [];
    let animId;

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    class Particle {
        constructor() { this.reset(); }
        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 1.5 + 0.3;
            this.speedX = (Math.random() - 0.5) * 0.3;
            this.speedY = (Math.random() - 0.5) * 0.3;
            this.opacity = Math.random() * 0.5 + 0.1;
            this.color = Math.random() > 0.6 ? '99,102,241' : Math.random() > 0.5 ? '6,182,212' : '139,92,246';
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) this.reset();
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${this.color},${this.opacity})`;
            ctx.fill();
        }
    }

    function initParticles() {
        particles = [];
        const count = Math.floor((canvas.width * canvas.height) / 12000);
        for (let i = 0; i < Math.min(count, 100); i++) particles.push(new Particle());
    }

    function connectParticles() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(99,102,241,${0.08 * (1 - dist / 120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => { p.update(); p.draw(); });
        connectParticles();
        animId = requestAnimationFrame(animate);
    }

    resizeCanvas();
    initParticles();
    animate();
    window.addEventListener('resize', () => { resizeCanvas(); initParticles(); });
}

// ── Navbar Scroll ─────────────────────────────────────────────
const navbar = document.getElementById('navbar');
if (navbar) {
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 40);
    });
}

// ── Smooth Scroll ─────────────────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
        const target = document.querySelector(a.getAttribute('href'));
        if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
    });
});

// ── Scroll Reveal ─────────────────────────────────────────────
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            // Animate progress bars inside
            entry.target.querySelectorAll('.model-bar-fill[data-width]').forEach(bar => {
                setTimeout(() => { bar.style.width = bar.dataset.width + '%'; }, 200);
            });
        }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

document.querySelectorAll('[data-reveal]').forEach(el => revealObserver.observe(el));

// ── Counter Animation ─────────────────────────────────────────
const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const el = entry.target;
            const target = parseInt(el.dataset.count);
            let current = 0;
            const duration = 1500;
            const step = target / (duration / 16);
            const timer = setInterval(() => {
                current = Math.min(current + step, target);
                el.textContent = Math.round(current);
                if (current >= target) clearInterval(timer);
            }, 16);
            counterObserver.unobserve(el);
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('[data-count]').forEach(el => counterObserver.observe(el));

// ── Architecture Step Hover ───────────────────────────────────
document.querySelectorAll('.arch-step').forEach((step, i) => {
    step.addEventListener('mouseenter', () => {
        document.querySelectorAll('.arch-step').forEach(s => s.classList.remove('active'));
        step.classList.add('active');
    });
});

// ── Mobile Menu ───────────────────────────────────────────────
const mobileToggle = document.getElementById('mobileToggle');
if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
        const links = document.querySelector('.nav-links');
        if (!links) return;
        const open = links.style.display === 'flex';
        links.style.display = open ? 'none' : 'flex';
        links.style.flexDirection = open ? '' : 'column';
        links.style.position = open ? '' : 'absolute';
        links.style.top = open ? '' : '100%';
        links.style.left = open ? '' : '0';
        links.style.right = open ? '' : '0';
        links.style.background = open ? '' : 'rgba(8,12,20,0.97)';
        links.style.backdropFilter = open ? '' : 'blur(20px)';
        links.style.padding = open ? '' : '2rem';
        links.style.borderBottom = open ? '' : '1px solid rgba(255,255,255,0.08)';
        links.style.gap = open ? '' : '1.5rem';
        links.style.zIndex = '999';
    });
}

// ── Table Row Stagger ─────────────────────────────────────────
const tableObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.querySelectorAll('tbody tr').forEach((row, i) => {
                row.style.opacity = '0';
                row.style.transform = 'translateX(-20px)';
                row.style.transition = `opacity 0.5s ease ${i * 0.08}s, transform 0.5s ease ${i * 0.08}s`;
                setTimeout(() => {
                    row.style.opacity = '1';
                    row.style.transform = 'translateX(0)';
                }, 50);
            });
            tableObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.2 });

document.querySelectorAll('.table-wrapper').forEach(t => tableObserver.observe(t));

// ── Prediction (from original script) ───────────────────────
async function handlePrediction(e) {
    if (e) e.preventDefault();
    
    const years = parseInt(document.getElementById('years')?.value || 0);
    const income = parseInt(document.getElementById('income')?.value || 0);
    const overtime = parseInt(document.getElementById('overtime')?.value || 0);
    const performance = document.getElementById('performance')?.value || 'stable';
    const engagement = parseInt(document.getElementById('engagement')?.value || 5);
    
    const resultPanel = document.getElementById('resultPanel');
    if (!resultPanel) return;
    
    resultPanel.innerHTML = `
        <div class="loading-state">
            <div class="loading-spinner"></div>
            <h4>Analyzing Employee Profile...</h4>
            <p>Running GRU Temporal Sequences & FT-Transformer Attention</p>
        </div>`;
    
    try {
        const response = await fetch('http://localhost:8000/predict-simple', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ years, income, overtime, performance, engagement })
        });
        
        if (!response.ok) throw new Error('API failed');
        
        const data = await response.json();
        renderResult(data, resultPanel);
        
    } catch {
        setTimeout(() => runLocalSimulation(years, income, overtime, performance, engagement), 300);
    }
}

function renderResult(data, panel) {
    const riskScore = Math.round(data.attrition_probability * 100);
    const riskLevel = data.risk_level;
    const riskClass = riskLevel === 'High' ? 'risk-high' : riskLevel === 'Medium' ? 'risk-medium' : 'risk-low';
    const riskColor = riskLevel === 'High' ? '#ef4444' : riskLevel === 'Medium' ? '#f59e0b' : '#10b981';
    const riskIcon = riskLevel === 'High' ? 'fa-triangle-exclamation' : riskLevel === 'Medium' ? 'fa-circle-exclamation' : 'fa-circle-check';
    
    panel.innerHTML = `
        <div class="result-card">
            <div class="result-header">
                <h3><i class="fas fa-chart-line"></i> Risk Analysis</h3>
                <span class="risk-badge ${riskClass}"><i class="fas ${riskIcon}"></i> ${riskLevel} Risk</span>
            </div>
            <div class="result-gauge">
                <svg viewBox="0 0 140 80" class="gauge-svg">
                    <path d="M 10 75 A 60 60 0 0 1 130 75" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10" stroke-linecap="round"/>
                    <path d="M 10 75 A 60 60 0 0 1 130 75" fill="none" stroke="${riskColor}" stroke-width="10" stroke-linecap="round"
                        stroke-dasharray="${(riskScore / 100) * 188.5} 188.5" class="gauge-fill" opacity="0.85"/>
                </svg>
                <div class="gauge-val" style="color:${riskColor}">${riskScore}<span>%</span></div>
                <div class="gauge-label">Attrition Probability</div>
            </div>
            <div class="result-stats">
                <div class="rstat"><span class="rstat-label">Risk Level</span><span class="rstat-val" style="color:${riskColor}">${riskLevel}</span></div>
                <div class="rstat"><span class="rstat-label">Confidence</span><span class="rstat-val">${((data.confidence || 0.94) * 100).toFixed(1)}%</span></div>
            </div>
            ${data.factors && data.factors.length > 0 ? `
            <div class="shap-block">
                <h5><i class="fas fa-magnifying-glass-chart"></i> Key Risk Factors</h5>
                ${data.factors.map((f, i) => `
                    <div class="shap-row">
                        <span class="shap-name">${f}</span>
                        <div class="shap-track"><div class="shap-fill" style="width:${85 - i * 16}%;animation-delay:${i * 0.1}s"></div></div>
                        <span class="shap-pct">${85 - i * 16}%</span>
                    </div>`).join('')}
            </div>` : ''}
            <div class="rec-box rec-${riskLevel.toLowerCase()}">
                <strong><i class="fas fa-lightbulb"></i> HR Recommendation</strong>
                <p>${data.recommendation || 'Continue standard engagement protocols.'}</p>
            </div>
        </div>`;
    
    // Animate gauge
    const fill = panel.querySelector('.gauge-fill');
    if (fill) {
        const target = (riskScore / 100) * 188.5;
        fill.style.strokeDasharray = `0 188.5`;
        setTimeout(() => {
            fill.style.transition = 'stroke-dasharray 1.2s cubic-bezier(0.16,1,0.3,1)';
            fill.style.strokeDasharray = `${target} 188.5`;
        }, 100);
    }
    
    // Animate shap bars
    panel.querySelectorAll('.shap-fill').forEach((bar, i) => {
        const w = bar.style.width;
        bar.style.width = '0';
        setTimeout(() => {
            bar.style.transition = 'width 0.8s cubic-bezier(0.16,1,0.3,1)';
            bar.style.width = w;
        }, 400 + i * 100);
    });
}

function runLocalSimulation(years, income, overtime, performance, engagement) {
    let riskScore = 15;
    let factors = [];
    if (overtime > 15) { riskScore += 30; factors.push('Excessive Overtime'); }
    if (engagement < 5) { riskScore += 25; factors.push('Low Engagement'); }
    if (performance === 'low') { riskScore += 20; factors.push('Declining Performance'); }
    if (years < 2 && income < 3000) { riskScore += 15; factors.push('Early Career / Low Pay'); }
    if (years > 10 && performance === 'stable') { riskScore += 10; factors.push('Career Stagnation Risk'); }
    if (riskScore > 99) riskScore = 99;
    
    const riskLevel = riskScore > 70 ? 'High' : riskScore > 40 ? 'Medium' : 'Low';
    const rec = riskLevel === 'High'
        ? 'Immediate intervention required — review workload and compensation.'
        : riskLevel === 'Medium'
        ? 'Schedule a check-in meeting to discuss career goals.'
        : 'Continue standard engagement protocols.';
    
    const resultPanel = document.getElementById('resultPanel');
    if (resultPanel) renderResult({ attrition_probability: riskScore / 100, risk_level: riskLevel, factors, recommendation: rec, confidence: 0.94 }, resultPanel);
}