/**
 * BYOK LLM client — OpenAI-compatible streaming.
 * Port of claude_client.py adapted for browser fetch().
 */

const PROVIDER_PRESETS = {
    ollama: {
        name: 'Ollama',
        baseUrl: 'http://localhost:11434/v1',
        apiKey: '',
        defaultModel: 'llama3.2',
    },
    lmstudio: {
        name: 'LM Studio',
        baseUrl: 'http://localhost:1234/v1',
        apiKey: 'lm-studio',
        defaultModel: '',
    },
    claude: {
        name: 'Claude (local proxy)',
        baseUrl: 'http://localhost:8000/v1',
        apiKey: '',
        defaultModel: 'claude-sonnet-4-6',
    },
    openai: {
        name: 'OpenAI',
        baseUrl: 'https://api.openai.com/v1',
        apiKey: '',
        defaultModel: 'gpt-4o-mini',
    },
    custom: {
        name: 'Custom',
        baseUrl: '',
        apiKey: '',
        defaultModel: '',
    },
};

export { PROVIDER_PRESETS };

export class LLMClient {
    constructor() {
        this.load();
    }

    /** Load settings from localStorage. */
    load() {
        const saved = localStorage.getItem('llm_settings');
        if (saved) {
            const s = JSON.parse(saved);
            this.provider = s.provider || 'ollama';
            this.baseUrl = s.baseUrl || PROVIDER_PRESETS.ollama.baseUrl;
            this.apiKey = s.apiKey || '';
            this.model = s.model || PROVIDER_PRESETS.ollama.defaultModel;
        } else {
            this.provider = 'ollama';
            this.baseUrl = PROVIDER_PRESETS.ollama.baseUrl;
            this.apiKey = '';
            this.model = PROVIDER_PRESETS.ollama.defaultModel;
        }
    }

    /** Save settings to localStorage. */
    save() {
        localStorage.setItem('llm_settings', JSON.stringify({
            provider: this.provider,
            baseUrl: this.baseUrl,
            apiKey: this.apiKey,
            model: this.model,
        }));
    }

    /** Configure from provider preset. */
    setProvider(provider) {
        const preset = PROVIDER_PRESETS[provider];
        if (preset) {
            this.provider = provider;
            this.baseUrl = preset.baseUrl;
            if (provider !== 'custom') {
                this.apiKey = preset.apiKey;
                this.model = preset.defaultModel;
            }
        }
        this.save();
    }

    /** Check if LLM is configured (has a base URL). */
    isConfigured() {
        return !!this.baseUrl;
    }

    /** Test connection to the LLM endpoint. */
    async testConnection() {
        if (!this.baseUrl) return { ok: false, error: 'No base URL configured' };

        try {
            const headers = {};
            if (this.apiKey) headers['Authorization'] = `Bearer ${this.apiKey}`;

            const res = await fetch(`${this.baseUrl}/models`, {
                headers,
                signal: AbortSignal.timeout(5000),
            });

            if (res.ok) {
                const data = await res.json();
                const models = data.data?.map(m => m.id) || [];
                return { ok: true, models };
            }
            return { ok: false, error: `HTTP ${res.status}` };
        } catch (e) {
            return { ok: false, error: e.message };
        }
    }

    /**
     * Streaming chat completion.
     * Yields text chunks as they arrive.
     *
     * @param {string} systemPrompt
     * @param {string} userPrompt
     * @param {AbortSignal} [signal]
     * @returns {AsyncGenerator<string>}
     */
    async *stream(systemPrompt, userPrompt, signal, { maxTokens = 800, temperature = 0.3 } = {}) {
        const endpoint = `${this.baseUrl}/chat/completions`;
        const headers = { 'Content-Type': 'application/json' };
        if (this.apiKey) headers['Authorization'] = `Bearer ${this.apiKey}`;

        const body = {
            model: this.model,
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userPrompt },
            ],
            max_tokens: maxTokens,
            temperature,
            stream: true,
        };

        const res = await fetch(endpoint, {
            method: 'POST',
            headers,
            body: JSON.stringify(body),
            signal,
        });

        if (!res.ok) {
            throw new Error(`LLM API error: ${res.status} ${res.statusText}`);
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // keep incomplete line

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                const dataStr = line.slice(6).trim();
                if (dataStr === '[DONE]') return;

                try {
                    const data = JSON.parse(dataStr);
                    const content = data.choices?.[0]?.delta?.content;
                    if (content) yield content;
                } catch (e) {
                    // ignore parse errors
                }
            }
        }
    }

    /**
     * Non-streaming chat completion.
     * @param {string} systemPrompt
     * @param {string} userPrompt
     * @returns {Promise<string>}
     */
    async generate(systemPrompt, userPrompt) {
        const endpoint = `${this.baseUrl}/chat/completions`;
        const headers = { 'Content-Type': 'application/json' };
        if (this.apiKey) headers['Authorization'] = `Bearer ${this.apiKey}`;

        const body = {
            model: this.model,
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userPrompt },
            ],
            max_tokens: 800,
            temperature: 0.3,
            stream: false,
        };

        const res = await fetch(endpoint, {
            method: 'POST',
            headers,
            body: JSON.stringify(body),
        });

        if (!res.ok) throw new Error(`LLM API error: ${res.status}`);
        const data = await res.json();
        return data.choices?.[0]?.message?.content || '';
    }
}
