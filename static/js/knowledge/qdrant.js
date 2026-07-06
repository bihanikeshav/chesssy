/**
 * Qdrant Cloud client via Cloudflare Worker proxy.
 * The proxy handles CORS + API key — browser sends plain POST requests.
 */

const DEFAULT_PROXY_URL = 'https://qdrant.bihanikeshav.workers.dev';
const COLLECTION        = 'chess_theory';
const INFERENCE_MODEL   = 'sentence-transformers/all-minilm-l6-v2';

let PROXY_URL = localStorage.getItem('qdrant_proxy_url') || DEFAULT_PROXY_URL;

export function configureQdrant(proxyUrl) {
    PROXY_URL = proxyUrl;
    localStorage.setItem('qdrant_proxy_url', proxyUrl);
}

export function isQdrantConfigured() {
    return !!PROXY_URL;
}

// ---------------------------------------------------------------------------
// Core query — uses Qdrant inference API (text → embedding → search, server-side)
// ---------------------------------------------------------------------------

async function inferenceSearch(queryText, filter, limit) {
    try {
        const res = await fetch(`${PROXY_URL}/collections/${COLLECTION}/points/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: { text: queryText, model: INFERENCE_MODEL },
                filter,
                limit,
                with_payload: true,
            }),
            signal: AbortSignal.timeout(8000),
        });

        if (!res.ok) {
            console.warn('[Qdrant] inferenceSearch failed:', res.status);
            return null;
        }

        const data = await res.json();
        return (data.result?.points || []).map(p => ({
            title:       p.payload?.title       || '',
            content:     p.payload?.content     || '',
            category:    p.payload?.category    || '',
            subcategory: p.payload?.subcategory || '',
            difficulty:  p.payload?.difficulty  || '',
            score:       p.score,
        }));
    } catch (e) {
        console.warn('[Qdrant] inferenceSearch error:', e.message);
        return null;
    }
}

async function scrollSearch(filter, limit) {
    try {
        const res = await fetch(`${PROXY_URL}/collections/${COLLECTION}/points/scroll`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filter, limit, with_payload: true }),
            signal: AbortSignal.timeout(8000),
        });
        if (!res.ok) return [];
        const data = await res.json();
        return (data.result?.points || []).map(p => ({
            title:       p.payload?.title       || '',
            content:     p.payload?.content     || '',
            category:    p.payload?.category    || '',
            subcategory: p.payload?.subcategory || '',
            difficulty:  p.payload?.difficulty  || '',
        }));
    } catch (e) {
        console.warn('[Qdrant] scrollSearch error:', e.message);
        return [];
    }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Query chess theory by category + optional semantic text search.
 */
export async function queryTheory(categories, tags = [], limit = 3, queryText = '') {
    if (!isQdrantConfigured()) return [];

    // Inference search doesn't need filter — just use semantic text
    try {
        if (queryText) {
            const results = await inferenceSearch(queryText, undefined, limit);
            if (results !== null) return results;
        }
        // Fallback: scroll (needs payload index on Qdrant — may fail)
        return await scrollSearch(undefined, limit);
    } catch (err) {
        console.warn('[Qdrant] queryTheory error:', err.message);
        return [];
    }
}

/**
 * Get relevant theory for a position/move context.
 */
export async function getRelevantTheory(positionType, moveTags = [], queryHint = '') {
    const queryText = queryHint || [positionType, ...moveTags].join(' ');
    return queryTheory([], moveTags, 3, queryText);
}

/** No-op — kept for API compatibility. */
export function preloadEmbedder() {}
