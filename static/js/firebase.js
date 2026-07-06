/**
 * Firebase SDK initialisation.
 * Analytics is active by default. Other services (Auth, Firestore) are
 * exported as lazy helpers — call them only when needed.
 */

import { initializeApp } from 'https://www.gstatic.com/firebasejs/11.6.0/firebase-app.js';
import { getAnalytics, logEvent } from 'https://www.gstatic.com/firebasejs/11.6.0/firebase-analytics.js';

const firebaseConfig = {
    apiKey:            'AIzaSyAq_t2sOV2l7_Mw5qvA9eHr_TJAQUaKxgg',
    authDomain:        'chesssy.firebaseapp.com',
    projectId:         'chesssy',
    storageBucket:     'chesssy.firebasestorage.app',
    messagingSenderId: '465691595944',
    appId:             '1:465691595944:web:6c56361a53db87240e5e9d',
    measurementId:     'G-RY1XHH9Z4X',
};

const app       = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// ---------------------------------------------------------------------------
// Typed analytics events — call these from anywhere in the app
// ---------------------------------------------------------------------------

/** User played a move and analysis ran. */
export function trackMoveAnalyzed(quality, positionType) {
    logEvent(analytics, 'move_analyzed', { quality, position_type: positionType });
}

/** LLM explanation was generated (or fallback was used). */
export function trackExplanation(source) {
    // source: 'llm' | 'fallback'
    logEvent(analytics, 'explanation_generated', { source });
}

/** User asked a follow-up chat question. */
export function trackChat(contextMode) {
    // contextMode: 'move' | 'position' | 'hint'
    logEvent(analytics, 'chat_message', { context: contextMode });
}

/** User imported a game. */
export function trackImport(method) {
    // method: 'pgn' | 'fen' | 'lichess_url' | 'chesscom_url'
    logEvent(analytics, 'game_imported', { method });
}

/** Full coach report was generated. */
export function trackCoachReport(moveCount) {
    logEvent(analytics, 'coach_report', { move_count: moveCount });
}

/** User opened the LLM settings modal. */
export function trackSettingsOpened() {
    logEvent(analytics, 'settings_opened');
}

export { app, analytics };
