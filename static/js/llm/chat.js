/**
 * Follow-up Q&A chat handler.
 * Supports two context modes:
 * - 'move': Questions about the played move ("why this move?", "doesn't it block the f-pawn?")
 * - 'position': Questions about future moves ("what about Bc5?", "what should I play?")
 */

import { LLMClient } from './client.js';
import { HINT_SYSTEM } from './prompt.js';

// Regex to detect chess notation in user text
const CHESS_NOTATION_RE = /[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8][+#]?/g;

export class ChatHandler {
    constructor(llmClient) {
        this.llm = llmClient;
        this.history = []; // {role, content}
        this.currentFacts = null; // latest MoveFacts context
    }

    /** Set the current analysis context for follow-up questions. */
    setContext(facts) {
        this.currentFacts = facts;
    }

    /** Clear conversation history. */
    clear() {
        this.history = [];
        this.currentFacts = null;
    }

    /**
     * Ask about the PLAYED MOVE (context = the move just analyzed).
     * The user is asking "why this move?" / "doesn't it weaken X?" etc.
     */
    async *askAboutMove(message, currentFen, skillMode = 'intermediate', signal) {
        const context = this._buildMoveContext(currentFen);
        const chatPrompts = this._getChatPrompts(skillMode);

        const systemPrompt = chatPrompts.move;
        yield* this._streamChat(systemPrompt, context, message, signal);
    }

    /**
     * Ask about FUTURE MOVES / position ideas.
     * The user is asking "what about Bc5?" / "should I push the e-pawn?" etc.
     */
    async *askAboutPosition(message, currentFen, skillMode = 'intermediate', signal) {
        const context = this._buildPositionContext(currentFen);
        const chatPrompts = this._getChatPrompts(skillMode);

        const systemPrompt = chatPrompts.position;
        yield* this._streamChat(systemPrompt, context, message, signal);
    }

    /**
     * Generate a hint about the current position for the side to move.
     * Uses engine lines to give a useful nudge without revealing the best move.
     */
    async *generateHint(currentFen, skillMode = 'intermediate', engineLines = null, signal) {
        const context = this._buildHintContext(currentFen, engineLines);

        if (!this.llm.isConfigured()) {
            yield this._generatePatternHint(engineLines);
            return;
        }

        try {
            for await (const chunk of this.llm.stream(HINT_SYSTEM, context, signal, { maxTokens: 80, temperature: 0.5 })) {
                yield chunk;
            }
        } catch (e) {
            if (e.name === 'AbortError') return;
            yield this._generatePatternHint(engineLines);
        }
    }

    // ===== Legacy method for backward compat =====
    async *ask(message, currentFen, skillMode = 'intermediate', signal) {
        yield* this.askAboutMove(message, currentFen, skillMode, signal);
    }

    // ===== Internal =====

    _buildMoveContext(currentFen) {
        if (!this.currentFacts) return `${currentFen.split(' ')[1] === 'w' ? 'White' : 'Black'} to move.`;
        const f = this.currentFacts;
        const parts = [
            `Move: ${f.playedMoveSan} (${f.moveQuality}).`,
            `Played by ${f.sideToMove}.`,
        ];
        if (f.cpLoss > 20) parts.push('This move lost some advantage.');
        if (f.bestMoveSan && f.bestMoveSan !== f.playedMoveSan) {
            parts.push(`Engine preferred: ${f.bestMoveSan}.`);
        }
        if (f.topLines?.length) {
            const alts = f.topLines.slice(0, 3).map(l =>
                `${(l.movesSan || []).slice(0, 5).join(' ')}`
            );
            parts.push(`Top lines: ${alts.join(' / ')}`);
        }
        return parts.join(' ');
    }

    _buildPositionContext(currentFen) {
        const side = currentFen.split(' ')[1] === 'w' ? 'White' : 'Black';
        const parts = [`${side} to move.`];
        if (this.currentFacts) {
            parts.push(`After: ${this.currentFacts.playedMoveSan}.`);
            if (this.currentFacts.positionType) parts.push(`Phase: ${this.currentFacts.positionType}.`);
            if (this.currentFacts.topLines?.length) {
                const lines = this.currentFacts.topLines.slice(0, 3).map(l =>
                    (l.movesSan || []).slice(0, 5).join(' ')
                );
                parts.push(`Engine lines: ${lines.join(' / ')}`);
            }
        }
        return parts.join(' ');
    }

    _getChatPrompts(skillMode) {
        const level = {
            beginner: { adj: 'a beginner', lang: 'Simple language.' },
            novice: { adj: 'a novice', lang: 'Simple language, explain terms.' },
            intermediate: { adj: 'an intermediate player', lang: 'Analytical, use variations.' },
            expert: { adj: 'a strong player', lang: 'Concise, deep variations.' },
        }[skillMode] || { adj: 'a player', lang: 'Clear and helpful.' };

        const moveTagRule = 'When mentioning specific chess moves, wrap them in <move> tags like <move>Nf3</move> so the student can click them to see them on the board.';
        return {
            move: `Chess coach for ${level.adj}. ${level.lang} User asks about the PLAYED MOVE — "it"/"this move" = the move just played. Reply in 2-3 sentences max. No bullet points. No numbered lists. No FEN. No headers. Never cite eval numbers. ${moveTagRule}`,
            position: `Chess coach for ${level.adj}. ${level.lang} User asks about FUTURE moves/plans. Reply in 2-3 sentences max. No bullet points. No numbered lists. No FEN. No headers. Never cite eval numbers. ${moveTagRule}`,
        };
    }

    async *_streamChat(systemPrompt, context, message, signal) {
        const moves = message.match(CHESS_NOTATION_RE) || [];
        if (moves.length) context += ` Moves mentioned: ${moves.join(', ')}.`;

        this.history.push({ role: 'user', content: message });

        const fullUser = `${context}\n\n${this._formatHistory()}`;

        if (!this.llm.isConfigured()) {
            const reply = 'Configure an LLM in Settings to enable chat. You can use Ollama, LM Studio, or any OpenAI-compatible API.';
            this.history.push({ role: 'assistant', content: reply });
            yield reply;
            return;
        }

        try {
            let fullResponse = '';
            for await (const chunk of this.llm.stream(systemPrompt, fullUser, signal, { maxTokens: 200 })) {
                fullResponse += chunk;
                yield chunk;
            }
            this.history.push({ role: 'assistant', content: fullResponse });
        } catch (e) {
            if (e.name === 'AbortError') return;
            const errMsg = `Error: ${e.message}. Check your LLM settings.`;
            this.history.push({ role: 'assistant', content: errMsg });
            yield errMsg;
        }
    }

    /**
     * Build minimal hint context — NO FEN, NO move names, only distilled clues.
     * The LLM must not see raw position data or it will try to "analyze" it.
     */
    _buildHintContext(fen, engineLines) {
        const side = fen.split(' ')[1] === 'w' ? 'White' : 'Black';
        const clues = [`${side} to move.`];

        if (engineLines && engineLines.length > 0) {
            const best = engineLines[0];
            const san = best.movesSan?.[0] || '';

            // What kind of move is best (without naming it)
            if (best.evalMate != null) clues.push('There is a forced checkmate available.');
            else if (san.includes('+')) clues.push('A forcing check is available.');
            else if (san.includes('x')) clues.push('A good capture is available.');
            else if (san.startsWith('O-')) clues.push('Castling could be important.');
            else if (san.startsWith('N')) clues.push('A knight can improve its position.');
            else if (san.startsWith('B')) clues.push('A bishop can become more active.');
            else if (san.startsWith('R')) clues.push('A rook move is best.');
            else if (san.startsWith('Q')) clues.push('The queen has a strong move.');
            else if (/^[a-h]/.test(san)) clues.push('A pawn move is best.');

            // Are there hanging pieces
            if (this.currentFacts?.threatsAfter?.hangingPieces?.length) {
                clues.push('There are undefended pieces.');
            }
            if (this.currentFacts?.tacticalMotifs?.length) {
                clues.push(`Tactical themes: ${this.currentFacts.tacticalMotifs.join(', ')}.`);
            }
        }

        if (this.currentFacts?.positionType) {
            clues.push(`Phase: ${this.currentFacts.positionType}.`);
        }

        return clues.join(' ');
    }

    /**
     * Rule-based fallback hint when no LLM is configured.
     */
    _generatePatternHint(engineLines) {
        if (!engineLines || !engineLines.length) {
            return 'Play a move and analyze the position first to get hints.';
        }

        const best = engineLines[0];
        const bestSan = best.movesSan?.[0] || '';

        if (best.evalMate != null) {
            return 'Look for a forcing sequence — there\'s a checkmate hidden in this position.';
        }
        if (bestSan.includes('+')) {
            return 'Have you considered all the checks? Sometimes the most direct move is best.';
        }
        if (bestSan.includes('x')) {
            return 'There might be a favorable exchange. Look at what you can capture and what it costs.';
        }
        if (bestSan.startsWith('O-')) {
            return 'King safety matters. Is your king well protected?';
        }
        if (bestSan.startsWith('N')) {
            return 'Think about your knights — is there a more active square for one of them?';
        }
        if (bestSan.startsWith('B')) {
            return 'One of your bishops might be able to find a stronger diagonal.';
        }
        if (bestSan.startsWith('R')) {
            return 'Look at your rooks — are they on open files or connected?';
        }
        if (bestSan.startsWith('Q')) {
            return 'Your queen might have a powerful move. Look for active squares.';
        }
        if (/^[a-h]/.test(bestSan)) {
            return 'Consider a pawn move — sometimes a small push changes everything.';
        }

        // Check for hanging pieces in facts
        if (this.currentFacts?.threatsAfter?.hangingPieces?.length) {
            return 'Look carefully — there\'s an undefended piece. Can you take advantage of it?';
        }
        if (this.currentFacts?.positionType === 'opening') {
            return 'In the opening, focus on developing pieces, controlling the center, and king safety.';
        }

        return 'Take your time and look for your opponent\'s weaknesses before choosing a move.';
    }

    _formatHistory() {
        return this.history.slice(-8).map(m =>
            `${m.role === 'user' ? 'Player' : 'Coach'}: ${m.content}`
        ).join('\n');
    }
}
