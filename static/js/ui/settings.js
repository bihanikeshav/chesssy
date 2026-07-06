/**
 * BYOK Settings modal — LLM provider config, test connection, Lichess auth.
 */

import { PROVIDER_PRESETS } from '../llm/client.js';
import { trackSettingsOpened } from '../firebase.js';
import { setLichessToken, getLichessToken } from '../knowledge/explorer.js';
import { loginWithLichess, getLichessUser, logoutLichess } from '../knowledge/lichess-auth.js';

let llmClient = null;
let modalEl = null;

/**
 * Initialize the settings modal.
 * @param {LLMClient} client
 */
export function initSettings(client) {
    llmClient = client;
    modalEl = document.getElementById('settings-modal');

    // Provider dropdown
    const providerSelect = document.getElementById('settings-provider');
    if (providerSelect) {
        providerSelect.addEventListener('change', () => {
            const provider = providerSelect.value;
            llmClient.setProvider(provider);
            populateFields();
        });
    }

    // Save button
    const saveBtn = document.getElementById('settings-save');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveSettings);
    }

    // Test button
    const testBtn = document.getElementById('settings-test');
    if (testBtn) {
        testBtn.addEventListener('click', testConnection);
    }

    // Close
    const closeBtn = document.getElementById('settings-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeSettings);
    }

    // Click outside to close
    if (modalEl) {
        modalEl.addEventListener('click', (e) => {
            if (e.target === modalEl) closeSettings();
        });
    }

    // Gear button
    const gearBtn = document.getElementById('btn-settings');
    if (gearBtn) {
        gearBtn.addEventListener('click', () => {
            trackSettingsOpened();
            openSettings();
        });
    }

    // Lichess login/logout
    const lichessLoginBtn = document.getElementById('btn-lichess-login');
    if (lichessLoginBtn) {
        lichessLoginBtn.addEventListener('click', () => loginWithLichess());
    }

    const lichessLogoutBtn = document.getElementById('btn-lichess-logout');
    if (lichessLogoutBtn) {
        lichessLogoutBtn.addEventListener('click', async () => {
            await logoutLichess(getLichessToken());
            updateLichessStatus();
        });
    }

    // Update Lichess status on init
    updateLichessStatus();
}

/** Open settings modal. */
export function openSettings() {
    if (!modalEl) return;
    populateFields();
    updateLichessStatus();
    modalEl.classList.add('active');
}

/** Close settings modal. */
export function closeSettings() {
    if (modalEl) modalEl.classList.remove('active');
}

/** Update Lichess auth display after OAuth callback. */
export function refreshLichessStatus() {
    updateLichessStatus();
}

function populateFields() {
    const provider = document.getElementById('settings-provider');
    const baseUrl = document.getElementById('settings-baseurl');
    const apiKey = document.getElementById('settings-apikey');
    const model = document.getElementById('settings-model');
    const lichessToken = document.getElementById('settings-lichess-token');

    if (provider) provider.value = llmClient.provider;
    if (baseUrl) baseUrl.value = llmClient.baseUrl;
    if (apiKey) apiKey.value = llmClient.apiKey;
    if (model) model.value = llmClient.model;
    if (lichessToken) lichessToken.value = getLichessToken();
}

async function updateLichessStatus() {
    const statusEl = document.getElementById('lichess-status-text');
    const loginBtn = document.getElementById('btn-lichess-login');
    const logoutBtn = document.getElementById('btn-lichess-logout');

    const token = getLichessToken();
    if (!token) {
        if (statusEl) statusEl.textContent = 'Not connected';
        if (statusEl) statusEl.className = '';
        if (loginBtn) loginBtn.style.display = '';
        if (logoutBtn) logoutBtn.style.display = 'none';
        return;
    }

    // We have a token — try to get username
    if (statusEl) statusEl.textContent = 'Checking...';

    const user = await getLichessUser(token);
    if (user && user.username) {
        if (statusEl) {
            statusEl.textContent = `Logged in as ${user.username}`;
            statusEl.className = 'lichess-connected';
        }
        if (loginBtn) loginBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = '';
    } else {
        // Token exists but might be a manual token (no /api/account access)
        if (statusEl) {
            statusEl.textContent = 'Token configured';
            statusEl.className = 'lichess-connected';
        }
        if (loginBtn) loginBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = '';
    }
}

function saveSettings() {
    const baseUrl = document.getElementById('settings-baseurl')?.value?.trim();
    const apiKey = document.getElementById('settings-apikey')?.value?.trim();
    const model = document.getElementById('settings-model')?.value?.trim();
    const provider = document.getElementById('settings-provider')?.value;

    if (baseUrl) llmClient.baseUrl = baseUrl;
    llmClient.apiKey = apiKey || '';
    if (model) llmClient.model = model;
    if (provider) llmClient.provider = provider;
    llmClient.save();

    // Save Lichess token (manual entry)
    const lichessToken = document.getElementById('settings-lichess-token')?.value?.trim();
    if (lichessToken !== undefined) {
        setLichessToken(lichessToken || '');
    }

    updateLichessStatus();

    const status = document.getElementById('settings-status');
    if (status) {
        status.textContent = 'Settings saved.';
        status.className = 'settings-status success';
    }
}

async function testConnection() {
    const status = document.getElementById('settings-status');
    const testBtn = document.getElementById('settings-test');

    if (status) {
        status.textContent = 'Testing...';
        status.className = 'settings-status';
    }
    if (testBtn) testBtn.disabled = true;

    // Temporarily apply unsaved field values for the test
    const origBase = llmClient.baseUrl;
    const origKey = llmClient.apiKey;
    const origModel = llmClient.model;

    llmClient.baseUrl = document.getElementById('settings-baseurl')?.value?.trim() || origBase;
    llmClient.apiKey = document.getElementById('settings-apikey')?.value?.trim() || '';
    llmClient.model = document.getElementById('settings-model')?.value?.trim() || origModel;

    const result = await llmClient.testConnection();

    // Restore
    llmClient.baseUrl = origBase;
    llmClient.apiKey = origKey;
    llmClient.model = origModel;

    if (testBtn) testBtn.disabled = false;

    if (result.ok) {
        const modelList = result.models?.slice(0, 5).join(', ') || 'connected';
        if (status) {
            status.textContent = `Connected! Models: ${modelList}`;
            status.className = 'settings-status success';
        }
    } else {
        if (status) {
            status.textContent = `Failed: ${result.error}`;
            status.className = 'settings-status error';
        }
    }
}
