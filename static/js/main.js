/**
 * ChessCoach v2 — Main entry point.
 * Wires all modules together: board, engine, analysis, LLM, UI.
 */

import { initEngine, analyzeProgressive, stopAnalysis } from './engine/analysis.js';
import { formatEval } from './engine/stockfish.js';
import { extractFacts } from './coach/facts.js';
import { generateCoachReport } from './coach/report.js';
import { LLMClient } from './llm/client.js';
import { PromptBuilder } from './llm/prompt.js';
import { generateFallbackExplanation } from './llm/fallback.js';
import { ChatHandler } from './llm/chat.js';
import { queryExplorer } from './knowledge/explorer.js';
import { getRelevantTheory } from './knowledge/qdrant.js';
import { handleOAuthCallback } from './knowledge/lichess-auth.js';
import {
    initBoard, getGame, getBoard, getFen, flipBoard, resetBoard as resetBoardFn,
    setPosition, undoMove as undoBoardMove, playUci, setPlayerNames,
    drawArrow, clearArrows
} from './board.js';
import { updateEvalBar } from './ui/eval-bar.js';
import { initEvalGraph, setEvalData, clearEvalGraph } from './ui/eval-graph.js';
import { MoveTree, initMoveTreeUI, renderTree, highlightCurrentNode, setNodeQuality } from './ui/move-tree.js';
import {
    showAnalysisLoading, showAnalysisEmpty, showAnalysisResult,
    setExplanationText, showAiLoading, setAiAnalysisText
} from './ui/analysis-panel.js';
import { initInlineChat, clearChat } from './ui/chat-panel.js';
import { showCoachProgress, showCoachReport, showCoachEmpty } from './ui/coach-panel.js';
import { renderExplorer, updateOpeningName, showExplorerLoading } from './ui/explorer-panel.js';
import { initSettings, refreshLichessStatus } from './ui/settings.js';
import { parseImport } from './ui/import.js';
import { toast } from './ui/toast.js';
import {
    trackMoveAnalyzed, trackExplanation, trackImport, trackCoachReport, trackSettingsOpened,
} from './firebase.js';

// ===== Skill Level Config =====
const SKILL_LEVELS = {
    beginner:     { rating: 900,  label: 'Beginner',     range: '<1000' },
    novice:       { rating: 1200, label: 'Novice',       range: '1000–1400' },
    intermediate: { rating: 1600, label: 'Intermediate', range: '1400–1800' },
    expert:       { rating: 1900, label: 'Expert',       range: '1800+' },
};

// ===== State =====
let currentSkillLevel = localStorage.getItem('skill') || 'intermediate';
let currentRating = SKILL_LEVELS[currentSkillLevel]?.rating || 1600;
let deepEval = false;
let moveTree = new MoveTree();
let pgnMoves = [];     // flat list for imported games (used by coach report)
let gameAnalysisData = {};
let sseAbort = null;
let lastFacts = null;
let engineReady = false;
let latestEngineLines = null; // latest engine analysis for hint context
let analysisVersion = 0; // incremented on each new move/navigation — stale results discarded

// ===== LLM =====
const llmClient = new LLMClient();
const promptBuilder = new PromptBuilder(currentSkillLevel);
const chatHandler = new ChatHandler(llmClient);

// ===== Init =====
document.addEventListener('DOMContentLoaded', async () => {
    // Handle Lichess OAuth callback (if redirected back with ?code=)
    const oauthHandled = await handleOAuthCallback();
    if (oauthHandled) {
        toast('Lichess login successful!', 'success');
    }

    // Board
    initBoard(onMoveMade);

    // Move tree
    initMoveTreeUI(document.getElementById('move-list'), onTreeNavigate);

    // Inline chat instances (two contexts + hint per panel)
    initInlineChat('analysis', {
        moveMessagesEl:     document.getElementById('analysis-move-messages'),
        moveInputEl:        document.getElementById('analysis-move-input'),
        moveSendBtn:        document.getElementById('analysis-move-send'),
        positionMessagesEl: document.getElementById('analysis-position-messages'),
        positionInputEl:    document.getElementById('analysis-position-input'),
        positionSendBtn:    document.getElementById('analysis-position-send'),
        hintBtn:            document.getElementById('analysis-hint-btn'),
        onAskAboutMove:     (msg, signal) => chatHandler.askAboutMove(msg, getFen(), currentSkillLevel, signal),
        onAskAboutPosition: (msg, signal) => chatHandler.askAboutPosition(msg, getFen(), currentSkillLevel, signal),
        onHint:             (signal) => chatHandler.generateHint(getFen(), currentSkillLevel, latestEngineLines, signal),
    });
    initInlineChat('coach', {
        moveMessagesEl:     document.getElementById('coach-move-messages'),
        moveInputEl:        document.getElementById('coach-move-input'),
        moveSendBtn:        document.getElementById('coach-move-send'),
        positionMessagesEl: document.getElementById('coach-position-messages'),
        positionInputEl:    document.getElementById('coach-position-input'),
        positionSendBtn:    document.getElementById('coach-position-send'),
        hintBtn:            document.getElementById('coach-hint-btn'),
        onAskAboutMove:     (msg, signal) => chatHandler.askAboutMove(msg, getFen(), currentSkillLevel, signal),
        onAskAboutPosition: (msg, signal) => chatHandler.askAboutPosition(msg, getFen(), currentSkillLevel, signal),
        onHint:             (signal) => chatHandler.generateHint(getFen(), currentSkillLevel, latestEngineLines, signal),
    });

    // Settings
    initSettings(llmClient);

    // Eval graph
    const graphCanvas = document.getElementById('eval-graph-canvas');
    if (graphCanvas) initEvalGraph(graphCanvas, navGameIndex);

    // Event listeners
    setupListeners();
    setupKeyboard();

    // Restore saved settings
    restoreSettings();

    // Init Stockfish WASM
    setStatus('Loading engine...');
    try {
        await initEngine();
        engineReady = true;
        setStatus('Ready');
        fetchExplorer(getFen());
        startAnalysis(getFen());
    } catch (e) {
        setStatus('Engine failed to load');
        toast('Stockfish WASM failed to load. Check static/lib/stockfish/', 'error');
        console.error('Engine init error:', e);
    }
});

// ===== Event Listeners =====
function setupListeners() {
    $('#btn-flip').click(flipBoard);
    $('#btn-reset').click(doReset);
    $('#btn-undo').click(doUndo);
    $('#btn-import').click(handleImport);
    $('#import-input').on('keypress', e => { if (e.which === 13) handleImport(); });
    $('#btn-first').click(() => { moveTree.goToStart(); syncBoardToTree(); });
    $('#btn-prev').click(() => { moveTree.goBack(); syncBoardToTree(); });
    $('#btn-next').click(() => { moveTree.goForward(); syncBoardToTree(); });
    $('#btn-last').click(() => { moveTree.goToEnd(); syncBoardToTree(); });
    $('#btn-analyze-game').click(analyzeFullGame);

    // Skill toggle (4 levels)
    document.querySelectorAll('.skill-toggle button').forEach(btn => {
        btn.addEventListener('click', function () {
            const level = this.dataset.level;
            setSkillLevel(level);
        });
    });

    // Deep eval toggle
    const deepToggle = document.getElementById('deep-eval-toggle');
    if (deepToggle) {
        deepToggle.addEventListener('change', function () {
            deepEval = this.checked;
            // Re-run analysis with new depth
            startAnalysis(getFen());
        });
    }

    // Tabs (only 2 now: analysis / coach)
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function () {
            switchTab(this.dataset.tab);
        });
    });

    // Clickable moves in LLM responses — event delegation
    document.addEventListener('click', (e) => {
        const moveEl = e.target.closest('.clickable-move');
        if (!moveEl) return;
        const san = moveEl.dataset.san;
        if (!san) return;
        playMoveFromChat(san);
    });
}

function setupKeyboard() {
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        switch (e.key) {
            case 'ArrowLeft':
                e.preventDefault();
                moveTree.goBack();
                syncBoardToTree();
                break;
            case 'ArrowRight':
                e.preventDefault();
                moveTree.goForward();
                syncBoardToTree();
                break;
            case 'Home':
                e.preventDefault();
                moveTree.goToStart();
                syncBoardToTree();
                break;
            case 'End':
                e.preventDefault();
                moveTree.goToEnd();
                syncBoardToTree();
                break;
            case 'f':
                e.preventDefault();
                flipBoard();
                break;
        }
    });
}

// ===== Move Handling =====

/** Play a SAN move from a clickable element in chat/explanation. */
function playMoveFromChat(san) {
    const game = getGame();
    const m = game.move(san);
    if (!m) {
        toast(`Illegal move: ${san}`, 'warning');
        game.load(getFen()); // restore in case of partial state
        return;
    }
    // Emit through the normal move flow
    const uci = m.from + m.to + (m.promotion || '');
    const fen = game.fen();
    getBoard().position(fen);
    onMoveMade({ san: m.san, uci, fen, move: m });
}

async function onMoveMade({ san, uci, fen, move }) {
    const fenBefore = moveTree.currentNode.fen;

    // Add to move tree (creates variation if needed)
    const node = moveTree.addMove(san, uci, fen);
    renderTree(moveTree);
    document.getElementById('movelist-area')?.classList.add('active');

    // Show loading states immediately — don't wait for engine
    showAnalysisLoading();
    showExplorerLoading();
    switchTab('analysis');
    clearArrows();

    // Fire Lichess explorer instantly (parallel with engine)
    fetchExplorer(fen);

    const moveNumber = node.moveNumber;
    // Must await fact extraction before starting progressive analysis,
    // otherwise engine.stop() from progressive deepening kills the extraction.
    await analyzeMove(fenBefore, uci, moveNumber);
    startAnalysis(fen);
}

// ===== Tree Navigation =====
function onTreeNavigate(node) {
    moveTree.goTo(node);
    syncBoardToTree();
}

/**
 * Navigate to a specific index in the main line (for eval graph clicks).
 */
function navGameIndex(idx) {
    const mainLine = moveTree.getMainLineMoves();
    if (idx < 0) {
        moveTree.goToStart();
    } else if (idx < mainLine.length) {
        moveTree.goTo(mainLine[idx]);
    } else if (mainLine.length > 0) {
        moveTree.goTo(mainLine[mainLine.length - 1]);
    }
    syncBoardToTree();
}

/**
 * Sync the board position, highlights, and analysis to the current tree node.
 */
async function syncBoardToTree() {
    const node = moveTree.currentNode;
    const fen = node.fen;

    // Set board position
    setPosition(fen);
    highlightCurrentNode(moveTree);

    // Fire explorer immediately (parallel with everything else)
    fetchExplorer(fen);

    // Show analysis if available
    if (node === moveTree.root) {
        showAnalysisEmpty();
    } else if (gameAnalysisData[node.id]) {
        showAnalysisResult(gameAnalysisData[node.id]);
        const fallback = generateFallbackExplanation(gameAnalysisData[node.id], currentRating);
        setExplanationText(fallback);
    } else if (node.moveSan) {
        // Must await fact extraction before starting progressive analysis,
        // otherwise engine.stop() from progressive deepening kills the extraction.
        await analyzeMove(node.fenBefore, node.moveUci, node.moveNumber);
    }

    startAnalysis(fen);
}

// ===== Engine Analysis =====
function startAnalysis(fen) {
    if (!engineReady) return;
    clearArrows();

    const depths = deepEval ? [8, 14, 18, 22] : [8, 14, 18];

    analyzeProgressive(fen, (data) => {
        latestEngineLines = data.lines;
        updateEvalBar(data.lines[0]?.evalCp || 0, data.lines[0]?.evalMate);
        renderEngineLines(data.lines, data.depth);

        // Draw best move arrow
        if (data.lines[0]?.moves?.length >= 1) {
            const bestUci = data.lines[0].moves[0];
            drawArrow(bestUci.substring(0, 2), bestUci.substring(2, 4));
        }

        const depthLabel = `d${data.depth}`;
        document.getElementById('engine-depth').textContent = depthLabel;
        setStatus(depthLabel);
    }, depths);
}

/** Fetch explorer data for a position (fire-and-forget, renders when ready). */
function fetchExplorer(fen) {
    showExplorerLoading();
    queryExplorer(fen).then(data => {
        renderExplorer(data);
        if (data?.opening) updateOpeningName(data.opening);
        else updateOpeningName(null);
    });
}

function renderEngineLines(lines, depth) {
    const container = document.getElementById('engine-lines');
    if (!container) return;

    if (!lines || !lines.length) {
        container.innerHTML = '<div class="engine-placeholder"><span class="dot-loader"></span></div>';
        return;
    }

    container.innerHTML = '';
    for (const line of lines) {
        const ev = line.eval || formatEval(line.evalCp, line.evalMate);
        const moves = (line.movesSan || []).join(' ');
        const evalCls = line.evalCp > 50 ? 'positive' : line.evalCp < -50 ? 'negative' : 'neutral';

        const div = document.createElement('div');
        div.className = 'engine-line';
        div.dataset.uci = line.moves?.[0] || '';
        div.innerHTML = `
            <span class="line-eval ${evalCls}">${ev}</span>
            <span class="line-pv">${moves}</span>
        `;
        div.addEventListener('click', () => {
            const uci = div.dataset.uci;
            if (uci) {
                const m = playUci(uci);
                if (m) onMoveMade({ san: m.san, uci, fen: getFen(), move: m });
            }
        });
        container.appendChild(div);
    }
}

// ===== Move Analysis =====
async function analyzeMove(fen, moveUci, moveNumber) {
    if (!engineReady) return;

    // Cancel any in-flight LLM stream
    if (sseAbort) sseAbort.abort();

    const myVersion = ++analysisVersion;
    showAnalysisLoading();
    switchTab('analysis');

    try {
        const facts = await extractFacts(fen, moveUci, moveNumber, currentRating, currentSkillLevel);

        // If user navigated away while we were analyzing, discard stale result
        if (analysisVersion !== myVersion) return;

        lastFacts = facts;
        chatHandler.setContext(facts);

        // Cache analysis by node id
        gameAnalysisData[moveTree.currentNode.id] = facts;

        showAnalysisResult(facts);
        trackMoveAnalyzed(facts.moveQuality, facts.positionType);

        // Stream LLM explanation or use fallback
        streamExplanation(facts, myVersion);
    } catch (e) {
        if (analysisVersion !== myVersion) return;
        console.error('Analysis error:', e);
        showAnalysisEmpty();
        toast('Analysis failed: ' + e.message, 'error');
    }
}

async function streamExplanation(facts, version) {
    // Check version before even starting
    if (version !== undefined && analysisVersion !== version) return;

    // Rule-based explanation — always shown immediately
    const fallback = generateFallbackExplanation(facts, currentRating);
    setExplanationText(fallback);

    if (!llmClient.isConfigured()) {
        trackExplanation('fallback');
        return;
    }

    // Show AI analysis loading bar
    showAiLoading();

    // Fetch RAG context — must complete before LLM fires
    let ragPassages = [];
    try {
        ragPassages = await getRelevantTheory(facts.positionType, facts.playedMoveTags);
    } catch (e) {
        console.warn('[RAG] Failed:', e.message);
    }

    if (version !== undefined && analysisVersion !== version) return;

    // Build prompt with RAG data, then stream LLM into AI section
    const { system, user } = promptBuilder.build(facts, { ragPassages, playerRating: currentRating });

    // Cancel previous stream
    if (sseAbort) sseAbort.abort();
    sseAbort = new AbortController();

    try {
        let fullText = '';
        for await (const chunk of llmClient.stream(system, user, sseAbort.signal)) {
            if (version !== undefined && analysisVersion !== version) return;
            fullText += chunk;
            // Strip common LLM prefixes like "# Analysis:" or "## Analysis:"
            const displayText = fullText.replace(/^#+\s*Analysis:?\s*\n?/i, '').trimStart();
            setAiAnalysisText(displayText);
        }
        trackExplanation('llm');
    } catch (e) {
        if (e.name === 'AbortError') return;
        if (version !== undefined && analysisVersion !== version) return;
        // Hide AI section on error — fallback already showing
        trackExplanation('fallback');
    }
}

// ===== Import =====
async function handleImport() {
    const input = document.getElementById('import-input')?.value;
    if (!input) return;

    const btn = document.getElementById('btn-import');
    if (btn) { btn.disabled = true; btn.textContent = 'Loading...'; }

    const result = await parseImport(input);

    if (btn) { btn.disabled = false; btn.textContent = 'Import'; }

    if (result.error) {
        toast(result.error, 'error');
        return;
    }

    if (result.type === 'fen') {
        moveTree.reset(result.fen);
        setPosition(result.fen);
        pgnMoves = [];
        renderTree(moveTree);
        showAnalysisEmpty();
        startAnalysis(getFen());
        trackImport('fen');
        toast('FEN loaded', 'success');
        return;
    }

    if (result.type === 'pgn') {
        loadGameData(result);
        trackImport(result.source || 'pgn');
        toast('Game imported', 'success');
    }
}

function loadGameData(data) {
    pgnMoves = data.moves;
    gameAnalysisData = {};
    clearEvalGraph();

    const h = data.headers || {};
    const info = `${h.White || '?'} vs ${h.Black || '?'} \u2014 ${data.result || '*'}`;
    const gameInfoEl = document.getElementById('game-info');
    if (gameInfoEl) gameInfoEl.textContent = info;
    setPlayerNames(h.White || 'White', h.Black || 'Black');

    // Load into move tree
    moveTree.loadFromPgn(pgnMoves, 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1');

    // Build FEN data for each node by replaying moves
    const game = getGame();
    game.reset();
    const mainLine = moveTree.getMainLineMoves();
    for (const node of mainLine) {
        node.fenBefore = game.fen();
        const m = game.move(node.moveSan);
        if (m) {
            node.fen = game.fen();
            node.moveUci = m.from + m.to + (m.promotion || '');
        }
    }

    renderTree(moveTree);
    document.getElementById('movelist-area')?.classList.add('active');

    // Reset board to start
    setPosition(moveTree.root.fen);
    startAnalysis(getFen());
    setStatus('Ready');
}

// ===== Full Game Analysis =====
async function analyzeFullGame() {
    const mainLine = moveTree.getMainLineMoves();
    if (!mainLine.length || !engineReady) return;

    const btn = document.getElementById('btn-analyze-game');
    if (btn) { btn.disabled = true; btn.textContent = 'Analyzing...'; }
    gameAnalysisData = {};

    switchTab('coach');
    showCoachProgress(0, mainLine.length);

    try {
        // Build pgnMoves-compatible list from tree
        const movesForReport = mainLine.map(node => ({
            moveSan: node.moveSan,
            moveUci: node.moveUci,
            fenBefore: node.fenBefore,
            moveNumber: node.moveNumber,
            side: node.side,
        }));

        const report = await generateCoachReport(movesForReport, currentRating, currentSkillLevel,
            (current, total, facts) => {
                showCoachProgress(current, total);
                if (facts) {
                    const node = mainLine[current - 1];
                    if (node) {
                        gameAnalysisData[node.id] = facts;
                        node.quality = facts.moveQuality;
                        setNodeQuality(node.id, facts.moveQuality);
                    }
                }
            }
        );

        trackCoachReport(movesForReport.length);
        showCoachReport(report, (idx) => {
            switchTab('analysis');
            if (idx >= 0 && idx < mainLine.length) {
                moveTree.goTo(mainLine[idx]);
                syncBoardToTree();
            }
        });

        // Set eval graph data
        setEvalData(report.evalHistory);

    } catch (e) {
        console.error('Coach report error:', e);
        toast('Analysis failed: ' + e.message, 'error');
        showCoachEmpty();
    }

    if (btn) { btn.disabled = false; btn.textContent = 'Analyze Game'; }
}

// ===== Helpers =====
function doReset() {
    resetBoardFn();
    moveTree.reset();
    pgnMoves = [];
    gameAnalysisData = {};
    lastFacts = null;
    chatHandler.clear();
    clearChat();
    renderTree(moveTree);
    document.getElementById('movelist-area')?.classList.remove('active');
    showAnalysisEmpty();
    showCoachEmpty();
    clearEvalGraph();
    clearArrows();
    startAnalysis(getFen());
}

function doUndo() {
    if (moveTree.currentNode === moveTree.root) return;
    const m = undoBoardMove();
    if (m) {
        moveTree.goBack();
        highlightCurrentNode(moveTree);
        showAnalysisEmpty();
        clearArrows();
        startAnalysis(getFen());
    }
}

function setSkillLevel(level) {
    if (!SKILL_LEVELS[level]) return;
    currentSkillLevel = level;
    currentRating = SKILL_LEVELS[level].rating;
    promptBuilder.setSkillMode(level);
    localStorage.setItem('skill', level);

    document.querySelectorAll('.skill-toggle button').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.level === level);
    });
}

function switchTab(name) {
    document.querySelectorAll('.tab').forEach(t => {
        t.classList.toggle('active', t.dataset.tab === name);
    });
    document.querySelectorAll('.tab-content').forEach(c => {
        c.classList.toggle('active', c.id === `panel-${name}`);
    });
}

function setStatus(text) {
    const el = document.getElementById('status-text');
    if (el) el.textContent = text;
}

function restoreSettings() {
    const savedSkill = localStorage.getItem('skill');
    if (savedSkill && SKILL_LEVELS[savedSkill]) {
        currentSkillLevel = savedSkill;
        currentRating = SKILL_LEVELS[savedSkill].rating;
    }

    document.querySelectorAll('.skill-toggle button').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.level === currentSkillLevel);
    });
}
