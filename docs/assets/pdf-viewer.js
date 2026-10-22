(() => {
    'use strict';

    const viewer = document.querySelector('.viewer');
    const container = document.querySelector('.viewer-container');
    const surface = document.querySelector('.page-surface');
    const canvas = document.getElementById('pdf-canvas');
    const links = document.getElementById('pdf-links');
    const loading = document.getElementById('loading');
    const pageInput = document.getElementById('page-input');
    const pageInfo = document.getElementById('page-info');
    const zoomDisplay = document.getElementById('zoom-display');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const zoomOutBtn = document.getElementById('zoom-out-btn');
    const zoomInBtn = document.getElementById('zoom-in-btn');
    const fitBtn = document.getElementById('fit-btn');
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    const fullscreenMessage = document.getElementById('fullscreen-message');
    let previousView = null;
    let pdfDoc;
    let pageNum = 1;
    let scale = 1;
    let fitWidth = true;
    let rendering = false;
    let pending = false;

    function showError(error) {
        console.error('PDF viewer error:', error);
        loading.textContent = 'PDFを表示できませんでした。上のリンクからPDFをダウンロードしてご覧ください。';
        loading.classList.add('error');
        loading.hidden = false;
        surface.hidden = true;
        container.setAttribute('aria-busy', 'false');
        pageInfo.textContent = '表示エラー';
    }

    async function navigateTo(destination) {
        try {
            const dest = typeof destination === 'string' ? await pdfDoc.getDestination(destination) : destination;
            if (!dest) return;
            const index = typeof dest[0] === 'number' ? dest[0] : await pdfDoc.getPageIndex(dest[0]);
            goToPage(index + 1);
        } catch (error) {
            console.error('PDF link error:', error);
        }
    }

    async function renderLinks(page, viewport) {
        const annotations = await page.getAnnotations();
        links.replaceChildren();
        for (const annotation of annotations) {
            if (annotation.subtype !== 'Link' || (!annotation.url && !annotation.dest)) continue;
            const link = document.createElement('a');
            const [x1, y1, x2, y2] = viewport.convertToViewportRectangle(annotation.rect);
            Object.assign(link.style, {
                left: `${Math.min(x1, x2) / viewport.width * 100}%`,
                top: `${Math.min(y1, y2) / viewport.height * 100}%`,
                width: `${Math.abs(x2 - x1) / viewport.width * 100}%`,
                height: `${Math.abs(y2 - y1) / viewport.height * 100}%`
            });
            if (annotation.url) {
                link.href = annotation.url;
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
                link.title = annotation.url;
                link.setAttribute('aria-label', annotation.url);
            } else {
                link.href = '#pdf-canvas';
                link.setAttribute('aria-label', 'リンク先のスライドへ移動');
                link.addEventListener('click', event => {
                    event.preventDefault();
                    navigateTo(annotation.dest);
                });
            }
            links.appendChild(link);
        }
    }

    // Serialize rendering, including annotations, and keep the latest requested page/zoom.
    async function renderPage() {
        if (!pdfDoc) return;
        pending = true;
        if (rendering) return;
        rendering = true;
        try {
            while (pending) {
                pending = false;
                const num = pageNum;
                container.setAttribute('aria-busy', 'true');
                const page = await pdfDoc.getPage(num);
                if (fitWidth) {
                    const style = getComputedStyle(container);
                    const width = container.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
                    const original = page.getViewport({ scale: 1 });
                    scale = width / original.width;
                    if (document.fullscreenElement === viewer) {
                        const height = container.clientHeight - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom);
                        scale = Math.min(scale, height / original.height);
                    }
                }
                const viewport = page.getViewport({ scale });
                // Keep CSS dimensions independent of canvas pixels for crisp HiDPI rendering.
                const ratio = Math.min(window.devicePixelRatio || 1, 2);
                canvas.width = Math.ceil(viewport.width * ratio);
                canvas.height = Math.ceil(viewport.height * ratio);
                canvas.style.width = `${viewport.width}px`;
                canvas.style.height = `${viewport.height}px`;
                surface.style.width = `${viewport.width}px`;
                surface.style.height = `${viewport.height}px`;
                links.replaceChildren();
                await page.render({
                    canvasContext: canvas.getContext('2d'), viewport,
                    transform: [ratio, 0, 0, ratio, 0, 0]
                }).promise;
                await renderLinks(page, viewport);
                loading.hidden = true;
                surface.hidden = false;
                canvas.setAttribute('aria-label', `スライド ${num} / ${pdfDoc.numPages}`);
                pageInfo.textContent = `${String(num).padStart(2, '0')} / ${String(pdfDoc.numPages).padStart(2, '0')}`;
                pageInput.value = num;
                zoomDisplay.textContent = `${Math.round(scale * 100)}%`;
                prevBtn.disabled = num <= 1;
                nextBtn.disabled = num >= pdfDoc.numPages;
                zoomOutBtn.disabled = scale <= 0.25;
                zoomInBtn.disabled = scale >= 4;
                fitBtn.setAttribute('aria-pressed', String(fitWidth));
                container.setAttribute('aria-busy', 'false');
            }
        } catch (error) {
            showError(error);
        } finally {
            rendering = false;
        }
    }

    function goToPage(num) {
        if (!pdfDoc || !Number.isInteger(num) || num < 1 || num > pdfDoc.numPages) return;
        pageNum = num;
        renderPage();
    }

    function changeZoom(value) {
        if (!pdfDoc) return;
        fitWidth = false;
        scale = Math.min(4, Math.max(0.25, value));
        renderPage();
    }

    prevBtn.addEventListener('click', () => goToPage(pageNum - 1));
    nextBtn.addEventListener('click', () => goToPage(pageNum + 1));
    zoomOutBtn.addEventListener('click', () => changeZoom(scale - 0.25));
    zoomInBtn.addEventListener('click', () => changeZoom(scale + 0.25));
    document.getElementById('actual-size-btn').addEventListener('click', () => changeZoom(1));
    fitBtn.addEventListener('click', () => { fitWidth = true; renderPage(); });
    pageInput.addEventListener('change', () => {
        const num = Number(pageInput.value);
        if (pdfDoc && Number.isInteger(num) && num >= 1 && num <= pdfDoc.numPages) goToPage(num);
        else pageInput.value = pageNum;
    });
    document.addEventListener('keydown', event => {
        // Some embedded browsers deliver Escape to the page instead of exiting themselves.
        if (event.key === 'Escape' && document.fullscreenElement === viewer) {
            event.preventDefault();
            fullscreenBtn.click();
            return;
        }
        if (!pdfDoc || event.altKey || event.ctrlKey || event.metaKey || event.target.closest('input, textarea, select, button, a, [contenteditable]')) return;
        if (['ArrowLeft', 'ArrowUp'].includes(event.key)) {
            event.preventDefault();
            goToPage(pageNum - 1);
        } else if (['ArrowRight', 'ArrowDown', ' '].includes(event.key)) {
            event.preventDefault();
            goToPage(pageNum + 1);
        }
    });
    links.addEventListener('click', event => {
        if (event.target.closest('a')) return;
        const rect = links.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width;
        if (x < 0.3) goToPage(pageNum - 1);
        else if (x > 0.7) goToPage(pageNum + 1);
    });
    if (document.fullscreenEnabled && viewer.requestFullscreen) {
        fullscreenBtn.hidden = false;
    }
    fullscreenBtn.addEventListener('click', async () => {
        fullscreenMessage.textContent = '';
        fullscreenBtn.disabled = true;
        try {
            if (document.fullscreenElement === viewer) await document.exitFullscreen();
            else await viewer.requestFullscreen();
        } catch (error) {
            console.error('Fullscreen error:', error);
            fullscreenMessage.textContent = '全画面表示を切り替えられませんでした。';
            fullscreenBtn.title = fullscreenMessage.textContent;
        } finally {
            fullscreenBtn.disabled = false;
        }
    });
    document.addEventListener('fullscreenchange', () => {
        const fullscreen = document.fullscreenElement === viewer;
        if (fullscreen) {
            previousView = { scale, fitWidth };
            fitWidth = true;
            container.focus({ preventScroll: true });
        } else if (previousView) {
            ({ scale, fitWidth } = previousView);
            previousView = null;
            fullscreenBtn.focus({ preventScroll: true });
        } else {
            return;
        }
        fullscreenBtn.textContent = fullscreen ? '全画面を終了' : '全画面';
        fullscreenBtn.setAttribute('aria-pressed', String(fullscreen));
        fullscreenBtn.title = fullscreen ? '全画面を終了（Esc）' : '全画面';
        fitBtn.textContent = fullscreen ? '全体を表示' : '幅に合わせる';
        container.scrollTop = 0;
        container.scrollLeft = 0;
        renderPage();
    });

    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => { if (fitWidth) renderPage(); }, 120);
    });

    async function init() {
        try {
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            pdfDoc = await pdfjsLib.getDocument(viewer.dataset.pdfUrl).promise;
            document.getElementById('total-pages').textContent = pdfDoc.numPages;
            pageInput.max = pdfDoc.numPages;
            pageInput.disabled = false;
            document.querySelectorAll('.zoom-controls button').forEach(button => { button.disabled = false; });
            await renderPage();
        } catch (error) {
            showError(error);
        }
    }
    init();
})();
