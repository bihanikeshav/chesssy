/**
 * Toast notification system.
 */

const TOAST_DURATION = 3500;

/**
 * Show a toast notification.
 * @param {string} message
 * @param {'info'|'success'|'error'|'warning'} [type='info']
 */
export function toast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = message;
    container.appendChild(el);

    // Trigger animation
    requestAnimationFrame(() => el.classList.add('show'));

    setTimeout(() => {
        el.classList.remove('show');
        el.addEventListener('transitionend', () => el.remove());
        // Fallback removal
        setTimeout(() => el.remove(), 300);
    }, TOAST_DURATION);
}
