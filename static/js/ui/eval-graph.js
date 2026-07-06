/**
 * Eval graph — line chart over all moves in a game.
 * Renders on a canvas element with filled area above/below midline.
 */

let canvas = null;
let ctx = null;
let evalData = []; // [{moveIndex, evalCp, quality}]
let onClickMove = null;

/**
 * Initialize the eval graph.
 * @param {HTMLCanvasElement} canvasEl
 * @param {function} clickHandler - called with moveIndex on click
 */
export function initEvalGraph(canvasEl, clickHandler) {
    canvas = canvasEl;
    ctx = canvas.getContext('2d');
    onClickMove = clickHandler;

    canvas.addEventListener('click', handleClick);

    // Resize observer
    const ro = new ResizeObserver(() => render());
    ro.observe(canvas.parentElement);
}

/**
 * Set eval data and re-render.
 * @param {object[]} data - Array of {moveIndex, evalCp, quality}
 */
export function setEvalData(data) {
    evalData = data;
    const area = document.getElementById('eval-graph-area');
    if (area) area.style.display = data && data.length ? '' : 'none';
    render();
}

/** Clear the graph. */
export function clearEvalGraph() {
    evalData = [];
    if (ctx && canvas) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    const area = document.getElementById('eval-graph-area');
    if (area) area.style.display = 'none';
}

function render() {
    if (!canvas || !ctx || !evalData.length) return;

    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    const w = canvas.width;
    const h = canvas.height;
    const midY = h / 2;
    const maxCp = 500; // clamp range

    ctx.clearRect(0, 0, w, h);

    // Background
    ctx.fillStyle = '#1e1e22';
    ctx.fillRect(0, 0, w, h);

    // Midline
    ctx.strokeStyle = '#444';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(0, midY);
    ctx.lineTo(w, midY);
    ctx.stroke();
    ctx.setLineDash([]);

    if (evalData.length < 2) return;

    const stepX = w / (evalData.length - 1);

    // Build points
    const points = evalData.map((d, i) => {
        const cp = d.evalCp != null ? Math.max(-maxCp, Math.min(maxCp, d.evalCp)) : 0;
        const y = midY - (cp / maxCp) * (midY - 4);
        return { x: i * stepX, y };
    });

    // Fill area above midline (white advantage) and below (black advantage)
    // White area (above midline = positive eval)
    ctx.beginPath();
    ctx.moveTo(points[0].x, midY);
    for (const p of points) {
        ctx.lineTo(p.x, Math.min(p.y, midY));
    }
    ctx.lineTo(points[points.length - 1].x, midY);
    ctx.closePath();
    ctx.fillStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.fill();

    // Black area (below midline = negative eval)
    ctx.beginPath();
    ctx.moveTo(points[0].x, midY);
    for (const p of points) {
        ctx.lineTo(p.x, Math.max(p.y, midY));
    }
    ctx.lineTo(points[points.length - 1].x, midY);
    ctx.closePath();
    ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
    ctx.fill();

    // Main line
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.strokeStyle = '#c9a84c';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Quality dots for mistakes/blunders
    for (let i = 0; i < evalData.length; i++) {
        const q = evalData[i].quality;
        if (q === 'blunder' || q === 'mistake') {
            ctx.beginPath();
            ctx.arc(points[i].x, points[i].y, 4, 0, Math.PI * 2);
            ctx.fillStyle = q === 'blunder' ? '#e05656' : '#e09b56';
            ctx.fill();
        }
    }
}

function handleClick(e) {
    if (!evalData.length || !onClickMove) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const stepX = canvas.width / (evalData.length - 1 || 1);
    const idx = Math.round(x / stepX);
    const clampedIdx = Math.max(0, Math.min(evalData.length - 1, idx));

    onClickMove(clampedIdx);
}
