/**
 * Lichess OAuth2 PKCE flow for browser-based apps.
 * No client_secret needed — uses code_challenge (S256).
 *
 * Flow:
 *   1. loginWithLichess() — generates PKCE pair, redirects to lichess.org/oauth
 *   2. On redirect back, handleOAuthCallback() exchanges code for access_token
 *   3. Token is passed to explorer.js via setLichessToken()
 */

import { setLichessToken } from './explorer.js';

const LICHESS_HOST = 'https://lichess.org';

// ---- PKCE helpers ----

function base64UrlEncode(bytes) {
    return btoa(String.fromCharCode(...bytes))
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');
}

function generateCodeVerifier() {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return base64UrlEncode(array);
}

async function generateCodeChallenge(verifier) {
    const data = new TextEncoder().encode(verifier);
    const hash = await crypto.subtle.digest('SHA-256', data);
    return base64UrlEncode(new Uint8Array(hash));
}

function getRedirectUri() {
    // Use origin + pathname (without query/hash)
    return window.location.origin + window.location.pathname;
}

// ---- Public API ----

/**
 * Redirect to Lichess OAuth page.
 * The user authorizes, Lichess redirects back with ?code=...
 */
export async function loginWithLichess() {
    const codeVerifier = generateCodeVerifier();
    const codeChallenge = await generateCodeChallenge(codeVerifier);

    // Persist verifier for the callback (survives redirect)
    sessionStorage.setItem('lichess_pkce_verifier', codeVerifier);

    const params = new URLSearchParams({
        response_type: 'code',
        client_id:     getRedirectUri(),   // Lichess accepts origin URL as client_id for PKCE
        redirect_uri:  getRedirectUri(),
        code_challenge_method: 'S256',
        code_challenge: codeChallenge,
        scope: '',                         // explorer needs no special scopes
    });

    window.location.href = `${LICHESS_HOST}/oauth?${params}`;
}

/**
 * Check URL for OAuth callback params and exchange code for token.
 * Call this on page load. Returns true if a callback was handled.
 */
export async function handleOAuthCallback() {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    if (!code) return false;

    const codeVerifier = sessionStorage.getItem('lichess_pkce_verifier');
    if (!codeVerifier) {
        console.warn('[LichessAuth] Got ?code= but no PKCE verifier in session');
        cleanUrl();
        return false;
    }

    sessionStorage.removeItem('lichess_pkce_verifier');
    cleanUrl();

    try {
        const res = await fetch(`${LICHESS_HOST}/api/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
                grant_type:    'authorization_code',
                code,
                redirect_uri:  getRedirectUri(),
                client_id:     getRedirectUri(),
                code_verifier: codeVerifier,
            }),
        });

        if (!res.ok) {
            const text = await res.text();
            console.error('[LichessAuth] Token exchange failed:', res.status, text);
            return false;
        }

        const data = await res.json();
        const token = data.access_token;
        if (!token) {
            console.error('[LichessAuth] No access_token in response');
            return false;
        }

        // Store token for explorer.js
        setLichessToken(token);
        console.log('[LichessAuth] Login successful');
        return true;
    } catch (e) {
        console.error('[LichessAuth] OAuth error:', e);
        return false;
    }
}

/**
 * Fetch current Lichess user info (to show username in UI).
 * Returns { username, ... } or null.
 */
export async function getLichessUser(token) {
    if (!token) return null;
    try {
        const res = await fetch(`${LICHESS_HOST}/api/account`, {
            headers: { 'Authorization': `Bearer ${token}` },
            signal: AbortSignal.timeout(5000),
        });
        if (!res.ok) return null;
        return await res.json();
    } catch {
        return null;
    }
}

/**
 * Revoke the current Lichess token (logout).
 */
export async function logoutLichess(token) {
    if (!token) return;
    try {
        await fetch(`${LICHESS_HOST}/api/token`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
        });
    } catch {
        // best-effort
    }
    setLichessToken('');
}

// ---- Internal ----

function cleanUrl() {
    // Remove ?code=...&state=... from URL without triggering a reload
    const clean = window.location.pathname + window.location.hash;
    window.history.replaceState({}, '', clean);
}
