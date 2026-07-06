/**
 * Lichess Opening Explorer API client.
 * Requires a Lichess personal API token (since Feb 2026).
 * Get one at: https://lichess.org/account/oauth/token
 */

const EXPLORER_BASE = 'https://explorer.lichess.ovh/lichess';
const CACHE = new Map();

// Serializing request queue
let _requestQueue = Promise.resolve();
const MIN_INTERVAL_MS = 1500;

// Lichess API token — stored in localStorage
let _lichessToken = localStorage.getItem('lichess_token') || '';

const RATING_BANDS = [0, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2500];

/** Configure the Lichess API token. */
export function setLichessToken(token) {
    _lichessToken = token;
    localStorage.setItem('lichess_token', token);
    CACHE.clear(); // clear cache so new token is used
}

/** Get current Lichess token. */
export function getLichessToken() {
    return _lichessToken;
}

/** Check if Lichess explorer is configured (has token). */
export function isExplorerConfigured() {
    return !!_lichessToken;
}

function getRatingBands(playerRating) {
    let closest = RATING_BANDS[0];
    for (const band of RATING_BANDS) {
        if (Math.abs(band - playerRating) < Math.abs(closest - playerRating)) {
            closest = band;
        }
    }
    const idx = RATING_BANDS.indexOf(closest);
    const bands = [closest];
    if (idx > 0) bands.unshift(RATING_BANDS[idx - 1]);
    if (idx < RATING_BANDS.length - 1) bands.push(RATING_BANDS[idx + 1]);
    return bands;
}

/**
 * Query the Lichess Opening Explorer for a position.
 * Returns null if no token configured or API fails.
 */
export function queryExplorer(fen) {
    if (!_lichessToken) return Promise.resolve(null);

    const key = 'broad:' + fen;
    if (CACHE.has(key)) return Promise.resolve(CACHE.get(key));

    return enqueueRequest(async () => {
        if (CACHE.has(key)) return CACHE.get(key);

        try {
            const params = new URLSearchParams({
                variant: 'standard',
                speeds: 'blitz,rapid,classical',
                ratings: '1600,1800,2000,2200,2500',
                fen,
            });

            const res = await fetchLichess(`${EXPLORER_BASE}?${params}`);
            if (!res || !res.ok) return null;

            const data = await res.json();
            const result = parseExplorerResponse(data);
            CACHE.set(key, result);
            return result;
        } catch (e) {
            console.warn('Explorer API error:', e.message);
            return null;
        }
    });
}

/**
 * Query explorer data for a specific player rating range.
 */
export function queryExplorerForRating(fen, playerRating) {
    if (!_lichessToken) return Promise.resolve(null);

    const bands = getRatingBands(playerRating);
    const key = `r${bands.join(',')}:${fen}`;
    if (CACHE.has(key)) return Promise.resolve(CACHE.get(key));

    return enqueueRequest(async () => {
        if (CACHE.has(key)) return CACHE.get(key);

        try {
            const params = new URLSearchParams({
                variant: 'standard',
                speeds: 'blitz,rapid,classical',
                ratings: bands.join(','),
                fen,
            });

            const res = await fetchLichess(`${EXPLORER_BASE}?${params}`);
            if (!res || !res.ok) return null;

            const data = await res.json();
            const result = parseExplorerResponse(data);
            CACHE.set(key, result);
            return result;
        } catch (e) {
            console.warn('Explorer API (rating-specific) error:', e.message);
            return null;
        }
    });
}

/**
 * Get the popularity of a specific move at the player's rating level.
 */
export async function getMovePopularity(fen, moveUci, playerRating) {
    const data = await queryExplorerForRating(fen, playerRating);
    if (!data || data.totalGames < 10) return null;

    const move = data.moves.find(m => m.uci === moveUci);
    const moveGames = move ? move.total : 0;

    return {
        popularity: moveGames / data.totalGames,
        totalGames: data.totalGames,
        moveGames,
    };
}

/**
 * Check if a position is "book" (≥100 games in DB).
 */
export async function isBookPosition(fen) {
    const result = await queryExplorer(fen);
    return result ? result.isBook : false;
}

export function clearExplorerCache() {
    CACHE.clear();
}

// ===== Internal =====

function parseExplorerResponse(data) {
    const totalGames = (data.white || 0) + (data.draws || 0) + (data.black || 0);

    return {
        white: data.white || 0,
        draws: data.draws || 0,
        black: data.black || 0,
        totalGames,
        moves: (data.moves || []).map(m => ({
            uci: m.uci,
            san: m.san,
            white: m.white || 0,
            draws: m.draws || 0,
            black: m.black || 0,
            total: (m.white || 0) + (m.draws || 0) + (m.black || 0),
            averageRating: m.averageRating || 0,
        })),
        opening: data.opening || null,
        isBook: totalGames >= 100,
    };
}

function enqueueRequest(fn) {
    _requestQueue = _requestQueue.then(async () => {
        const start = Date.now();
        const result = await fn();
        const elapsed = Date.now() - start;
        if (elapsed < MIN_INTERVAL_MS) {
            await new Promise(r => setTimeout(r, MIN_INTERVAL_MS - elapsed));
        }
        return result;
    });
    return _requestQueue;
}

/**
 * Fetch from Lichess with auth token and retry on 429.
 */
async function fetchLichess(url) {
    const headers = {};
    if (_lichessToken) {
        headers['Authorization'] = `Bearer ${_lichessToken}`;
    }

    try {
        let res = await fetch(url, {
            headers,
            signal: AbortSignal.timeout(8000),
        });

        if (res.status === 429) {
            await new Promise(r => setTimeout(r, 3000));
            res = await fetch(url, {
                headers,
                signal: AbortSignal.timeout(8000),
            });
        }

        return res;
    } catch (e) {
        console.warn('Lichess fetch error:', e.message);
        return null;
    }
}
