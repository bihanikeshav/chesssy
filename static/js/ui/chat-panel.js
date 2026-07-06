/**
 * Inline chat — two context types per panel:
 * 1. "Ask about this move" — questions about the played move
 * 2. "Explore next moves" — questions about future moves / position ideas
 * Plus a "Hint" button for getting guided hints.
 */

const chatInstances = {};

/**
 * Initialize an inline chat instance.
 * @param {string} id - Instance identifier
 * @param {object} config - {
 *   moveMessagesEl, moveInputEl, moveSendBtn,
 *   positionMessagesEl, positionInputEl, positionSendBtn,
 *   hintBtn,
 *   onAskAboutMove, onAskAboutPosition, onHint
 * }
 */
export function initInlineChat(id, config) {
    const instance = {
        ...config,
        abortController: null,
    };
    chatInstances[id] = instance;

    // "Ask about this move" input
    if (config.moveInputEl) {
        config.moveInputEl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage(id, 'move');
            }
        });
    }
    if (config.moveSendBtn) {
        config.moveSendBtn.addEventListener('click', () => sendMessage(id, 'move'));
    }

    // "Explore next moves" input
    if (config.positionInputEl) {
        config.positionInputEl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage(id, 'position');
            }
        });
    }
    if (config.positionSendBtn) {
        config.positionSendBtn.addEventListener('click', () => sendMessage(id, 'position'));
    }

    // Hint button
    if (config.hintBtn) {
        config.hintBtn.addEventListener('click', () => requestHint(id));
    }
}

/** Clear messages for a specific chat instance (or all). */
export function clearChat(id) {
    if (id) {
        const inst = chatInstances[id];
        if (inst?.moveMessagesEl) inst.moveMessagesEl.innerHTML = '';
        if (inst?.positionMessagesEl) inst.positionMessagesEl.innerHTML = '';
    } else {
        for (const key of Object.keys(chatInstances)) {
            clearChat(key);
        }
    }
}

async function sendMessage(id, type) {
    const inst = chatInstances[id];
    if (!inst) return;

    const inputEl = type === 'move' ? inst.moveInputEl : inst.positionInputEl;
    const messagesEl = type === 'move' ? inst.moveMessagesEl : inst.positionMessagesEl;
    const callback = type === 'move' ? inst.onAskAboutMove : inst.onAskAboutPosition;

    const msg = inputEl?.value?.trim();
    if (!msg || !callback) return;

    inputEl.value = '';

    appendMessage(messagesEl, 'user', msg);
    const assistantEl = appendMessage(messagesEl, 'assistant', '');

    if (inst.abortController) inst.abortController.abort();
    inst.abortController = new AbortController();

    try {
        let fullText = '';
        for await (const chunk of callback(msg, inst.abortController.signal)) {
            fullText += chunk;
            assistantEl.innerHTML = formatChat(fullText);
            scrollToBottom(messagesEl);
        }
    } catch (e) {
        if (e.name !== 'AbortError') {
            assistantEl.textContent = `Error: ${e.message}`;
        }
    }

    scrollToBottom(messagesEl);
}

async function requestHint(id) {
    const inst = chatInstances[id];
    if (!inst || !inst.onHint) return;

    // Show hint in the position messages area (bottom bar)
    const messagesEl = inst.positionMessagesEl || inst.moveMessagesEl;
    if (!messagesEl) return;

    const hintEl = appendMessage(messagesEl, 'assistant hint', '');

    if (inst.abortController) inst.abortController.abort();
    inst.abortController = new AbortController();

    try {
        let fullText = '';
        for await (const chunk of inst.onHint(inst.abortController.signal)) {
            fullText += chunk;
            hintEl.innerHTML = formatChat(fullText);
            scrollToBottom(messagesEl);
        }
    } catch (e) {
        if (e.name !== 'AbortError') {
            hintEl.textContent = 'Could not generate hint.';
        }
    }

    scrollToBottom(messagesEl);
}

function appendMessage(container, role, text) {
    if (!container) return document.createElement('div');
    const el = document.createElement('div');
    el.className = `chat-msg ${role}`;

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble';
    bubble.innerHTML = formatChat(text);
    el.appendChild(bubble);

    container.appendChild(el);
    scrollToBottom(container);
    return bubble;
}

function scrollToBottom(el) {
    const scrollArea = el?.closest('.tab-scroll-area');
    if (scrollArea) {
        scrollArea.scrollTop = scrollArea.scrollHeight;
    }
}

function formatChat(text) {
    return text
        // Complete <move>SAN</move> → clickable span
        .replace(/<move>([^<]+)<\/move>/g, '<span class="clickable-move" data-san="$1">$1</span>')
        // Strip incomplete move tags (streaming artifacts)
        .replace(/<\/?move[^>]*>?/g, '')
        // Markdown
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
}
