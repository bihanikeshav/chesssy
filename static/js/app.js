/**
 * ChessCoach — Frontend
 */

// ===== State =====
let board, game;
let currentFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
let moveHistory = [];
let pgnMoves = [];
let pgnIndex = -1;
let socket = null;
let currentRating = 1200;
let currentSkillLevel = 'intermediate';
let sseController = null;
let gameAnalysisData = {}; // index -> analysis data
let isFlipped = false;

// ===== Init =====
$(document).ready(function () {
    initBoard();
    initSocket();
    initListeners();
    initKeys();
});

function initBoard() {
    game = new Chess();
    board = Chessboard('board', {
        draggable: true,
        position: 'start',
        pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png',
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: () => board.position(game.fen()),
    });
    $(window).resize(() => board.resize());
}

function initSocket() {
    socket = io({ transports: ['websocket', 'polling'] });
    socket.on('connected', () => setStatus('Connected'));
    socket.on('connect', () => setTimeout(() => startAnalysis(currentFen), 200));
    socket.on('analysis_update', onAnalysisUpdate);
    socket.on('analysis_error', d => { console.error(d.error); setStatus('Error'); });
}

function initListeners() {
    $('#btn-flip').click(flipBoard);
    $('#btn-reset').click(resetBoard);
    $('#btn-undo').click(undoMove);
    $('#btn-import').click(handleImport);
    $('#import-input').on('keypress', e => { if (e.which === 13) handleImport(); });
    $('#btn-first').click(() => navGame(0));
    $('#btn-prev').click(() => navGame(pgnIndex - 1));
    $('#btn-next').click(() => navGame(pgnIndex + 1));
    $('#btn-last').click(() => navGame(pgnMoves.length - 1));
    $('#btn-analyze-game').click(analyzeFullGame);

    $('#rating-slider').on('input', function () {
        currentRating = +this.value;
        $('#rating-value').text(currentRating);
    });
    $('#rating-slider').on('change', function () {
        currentRating = +this.value;
        updateConfig();
    });

    // Tabs
    $('.tab').click(function () {
        const tab = $(this).data('tab');
        $('.tab').removeClass('active');
        $(this).addClass('active');
        $('.tab-content').removeClass('active');
        $(`#panel-${tab}`).addClass('active');
    });
}

function initKeys() {
    $(document).on('keydown', function (e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        switch (e.key) {
            case 'ArrowLeft': e.preventDefault(); pgnMoves.length ? navGame(pgnIndex - 1) : undoMove(); break;
            case 'ArrowRight': e.preventDefault(); if (pgnMoves.length) navGame(pgnIndex + 1); break;
            case 'Home': e.preventDefault(); if (pgnMoves.length) navGame(0); break;
            case 'End': e.preventDefault(); if (pgnMoves.length) navGame(pgnMoves.length - 1); break;
            case 'f': e.preventDefault(); flipBoard(); break;
        }
    });
}

// ===== Board handlers =====
function onDragStart(source, piece) {
    if (game.game_over()) return false;
    if ((game.turn() === 'w' && piece[0] === 'b') || (game.turn() === 'b' && piece[0] === 'w')) return false;
    return true;
}

function onDrop(source, target) {
    const piece = game.get(source);
    if (piece && piece.type === 'p') {
        const rank = target[1];
        if ((piece.color === 'w' && rank === '8') || (piece.color === 'b' && rank === '1')) {
            const test = game.move({ from: source, to: target, promotion: 'q' });
            if (!test) return 'snapback';
            game.undo();
            showPromoDialog(source, target, piece.color);
            return;
        }
    }
    const move = game.move({ from: source, to: target, promotion: 'q' });
    if (!move) return 'snapback';
    onMoveMade(move);
}

function showPromoDialog(source, target, color) {
    const pieces = ['q', 'r', 'b', 'n'];
    const prefix = color === 'w' ? 'w' : 'b';
    const names = { q: 'Q', r: 'R', b: 'B', n: 'N' };
    const c = $('#promotion-pieces').empty();
    pieces.forEach(p => {
        $(`<img class="promotion-piece" src="https://chessboardjs.com/img/chesspieces/wikipedia/${prefix}${names[p]}.png">`)
            .click(function () {
                const m = game.move({ from: source, to: target, promotion: p });
                if (m) { $('#promotion-overlay').removeClass('active'); board.position(game.fen()); onMoveMade(m); }
            }).appendTo(c);
    });
    $('#promotion-overlay').addClass('active');
}

function onMoveMade(move) {
    currentFen = game.fen();
    moveHistory.push(move);
    const uci = move.from + move.to + (move.promotion || '');
    analyzeMove(uci, moveHistory.length);
    startAnalysis(currentFen);
}

// ===== Analysis =====
function startAnalysis(fen) {
    if (socket && socket.connected) {
        socket.emit('start_analysis', { fen });
        setStatus('Analyzing...');
    }
}

function onAnalysisUpdate(data) {
    setStatus(`d${data.depth}`);
    updateEvalBar(data.eval_cp, data.eval_mate);
    renderEngineLines(data.lines);
    $('#engine-depth').text(`d${data.depth}`);
}

function analyzeMove(moveUci, moveNumber, fenBefore) {
    const fen = fenBefore || getFenBefore();
    showAnalysisLoading();

    $.post('/api/analyze_move', JSON.stringify({ fen, move: moveUci, move_number: moveNumber, player_rating: currentRating }),
        function (data) {
            if (data.error) { toast(data.error, 'error'); hideAnalysisLoading(); return; }
            showAnalysisResult(data);
            streamExplanation(fen, moveUci, moveNumber);
        }, 'json'
    ).fail(() => { toast('Analysis failed', 'error'); hideAnalysisLoading(); });
}

function streamExplanation(fen, move, moveNumber) {
    if (sseController) sseController.abort();
    sseController = new AbortController();
    const params = new URLSearchParams({ fen, move, move_number: moveNumber, player_rating: currentRating });
    let fullText = '';

    fetch(`/api/explain_stream?${params}`, { signal: sseController.signal })
        .then(res => {
            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let buf = '';
            function read() {
                reader.read().then(({ done, value }) => {
                    if (done) { if (fullText) $('#explanation').html(fmtExpl(fullText)); return; }
                    buf += decoder.decode(value, { stream: true });
                    const lines = buf.split('\n');
                    buf = lines.pop();
                    for (const line of lines) {
                        if (!line.startsWith('data: ')) continue;
                        try {
                            const d = JSON.parse(line.slice(6));
                            if (d.done || d.error) { $('#explanation').html(fmtExpl(fullText || d.error || '')); return; }
                            if (d.text) { fullText += d.text; $('#explanation').html(fmtExpl(fullText)); }
                        } catch (e) { }
                    }
                    read();
                }).catch(() => { if (fullText) $('#explanation').html(fmtExpl(fullText)); });
            }
            read();
        }).catch(() => { });
}

function fmtExpl(t) {
    return t.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>').replace(/\n/g, '<br>');
}

// ===== Display =====
function showAnalysisLoading() {
    $('#analysis-empty').hide();
    $('#analysis-content').hide();
    $('#analysis-loading').show();
    switchTab('analysis');
}

function hideAnalysisLoading() {
    $('#analysis-loading').hide();
}

function showAnalysisResult(d) {
    $('#analysis-loading').hide();
    $('#analysis-empty').hide();
    $('#analysis-content').show();

    $('#move-san').text(d.move_san);
    $('#quality-pill').text(d.quality).removeClass('best good inaccuracy mistake blunder').addClass(d.quality);

    const evB = fmtEval(d.eval_before), evA = fmtEval(d.eval_after);
    $('#eval-before').text(evB).removeClass('positive negative neutral').addClass(evalCls(d.eval_before));
    $('#eval-after').text(evA).removeClass('positive negative neutral').addClass(evalCls(d.eval_after));

    if (d.cp_loss > 0) {
        $('#cp-loss').text(`−${(d.cp_loss / 100).toFixed(1)}`).show();
    } else {
        $('#cp-loss').hide();
    }

    // Findability
    if (d.findability_score != null) {
        const pct = Math.round(d.findability_score * 100);
        const cls = pct >= 70 ? 'easy' : pct >= 40 ? 'medium' : 'hard';
        $('#find-bar').css('width', pct + '%').removeClass('easy medium hard').addClass(cls);
        $('#find-pct').text(pct + '%');
        const hints = { obvious: 'Most players would find this', natural: 'A natural candidate move',
            findable: 'Requires some thought', difficult: 'Hard to spot', 'engine-only': 'Only an engine finds this' };
        $('#find-hint').text(hints[d.findability_label] || d.findability_label || '');
        $('#find-meter').show();
    } else {
        $('#find-meter').hide();
    }

    // Explanation (fallback immediately, will be overwritten by stream)
    if (d.explanation_fallback) {
        $('#explanation').html(fmtExpl(d.explanation_fallback));
    }

    // Suggestion
    if (d.best_move_san && d.quality !== 'best' && d.quality !== 'good') {
        $('#suggestion-text').text(`Better was ${d.best_move_san}`);
        $('#suggestion-box').css('display', 'flex');
    } else {
        $('#suggestion-box').hide();
    }

    // Threats
    renderThreatTags(d);
}

function renderThreatTags(d) {
    const tags = [];
    if (d.tactical_motifs) d.tactical_motifs.forEach(m => tags.push({ text: m, cls: 'tactic' }));
    if (d.threats_created) d.threats_created.forEach(t => tags.push({ text: t, cls: 'warning' }));
    if (d.threats_ignored) d.threats_ignored.forEach(t => tags.push({ text: '⚠ ' + t, cls: 'danger' }));

    if (tags.length) {
        const list = $('#threats-list').empty();
        tags.slice(0, 6).forEach(t => list.append(`<span class="threat-tag ${t.cls}">${t.text}</span>`));
        $('#threats-area').show();
    } else {
        $('#threats-area').hide();
    }
}

function renderEngineLines(lines) {
    const c = $('#engine-lines').empty();
    if (!lines || !lines.length) { c.html('<div class="engine-placeholder"><span class="dot-loader"></span></div>'); return; }
    lines.forEach(line => {
        const ev = line.eval || fmtEval(line.eval_cp, line.eval_mate);
        const moves = line.moves_san ? line.moves_san.join(' ') : '';
        const uci = line.moves_uci ? line.moves_uci[0] : '';
        c.append(`<div class="engine-line" data-uci="${uci}">
            <span class="line-eval ${evalCls(line.eval_cp)}">${ev}</span>
            <span class="line-pv">${moves}</span>
            <span class="line-depth">d${line.depth}</span>
        </div>`);
    });
    c.find('.engine-line').click(function () { const u = $(this).data('uci'); if (u) playUci(u); });
}

// ===== Eval Bar =====
function updateEvalBar(cp, mate) {
    let pct, label;
    if (mate != null) {
        pct = mate > 0 ? 95 : 5;
        label = (mate > 0 ? '+' : '') + 'M' + Math.abs(mate);
    } else {
        const c = Math.max(-500, Math.min(500, cp || 0));
        pct = 50 + (c / 500) * 45;
        label = fmtEval(cp);
    }
    $('#eval-fill').css('height', pct + '%');
    $('#eval-label').text(label);
}

// ===== Import =====
function handleImport() {
    const input = $('#import-input').val().trim();
    if (!input) return;

    // Detect type
    if (input.includes('lichess.org') || input.includes('chess.com')) {
        importFromUrl(input);
    } else if (input.includes('[') || input.includes('1.')) {
        importPgn(input);
    } else if (input.includes('/') || input.includes(' ')) {
        loadFen(input);
    } else {
        toast('Paste a URL, PGN, or FEN', 'info');
    }
}

function importFromUrl(url) {
    setStatus('Importing...');
    $('#btn-import').prop('disabled', true).text('Loading...');

    $.post('/api/import_game', JSON.stringify({ url }), function (data) {
        $('#btn-import').prop('disabled', false).text('Import');
        if (data.error) { toast(data.error, 'error'); setStatus('Ready'); return; }
        loadGameData(data);
        toast('Game imported', 'success');
    }, 'json').fail(function () {
        $('#btn-import').prop('disabled', false).text('Import');
        toast('Import failed — try pasting the PGN directly', 'error');
        setStatus('Ready');
    });
}

function importPgn(pgnText) {
    setStatus('Loading...');
    $.post('/api/load_pgn', JSON.stringify({ pgn: pgnText }), function (data) {
        if (data.error) { toast(data.error, 'error'); setStatus('Ready'); return; }
        loadGameData(data);
        toast('Game loaded', 'success');
    }, 'json').fail(() => toast('Failed to parse PGN', 'error'));
}

function loadFen(fen) {
    try {
        if (!game.load(fen)) { toast('Invalid FEN', 'error'); return; }
        currentFen = fen;
        board.position(fen);
        moveHistory = [];
        pgnMoves = [];
        pgnIndex = -1;
        $('#movelist-area').removeClass('active');
        showEmpty();
        startAnalysis(currentFen);
    } catch (e) {
        toast('Invalid FEN', 'error');
    }
}

function loadGameData(data) {
    pgnMoves = data.moves;
    pgnIndex = -1;
    gameAnalysisData = {};

    const h = data.headers || {};
    const info = `${h.White || '?'} vs ${h.Black || '?'} — ${data.result || '*'}`;
    $('#game-info').text(info);
    updatePlayerNames(h.White || 'White', h.Black || 'Black');

    renderMoveList();
    $('#movelist-area').addClass('active');

    game.reset();
    board.position('start');
    currentFen = game.fen();
    moveHistory = [];
    startAnalysis(currentFen);
    setStatus('Ready');
}

function updatePlayerNames(white, black) {
    if (isFlipped) {
        $('#player-top-name').text(white);
        $('#player-bottom-name').text(black);
    } else {
        $('#player-top-name').text(black);
        $('#player-bottom-name').text(white);
    }
}

// ===== Move List =====
function renderMoveList() {
    const c = $('#move-list').empty();
    let num = 0;
    pgnMoves.forEach((m, i) => {
        if (m.side === 'white') { num++; c.append(`<span class="move-num">${num}.</span>`); }
        c.append(`<span class="move-cell" data-idx="${i}">${m.move_san}</span>`);
    });
    c.find('.move-cell').click(function () { navGame(+$(this).data('idx')); });
}

function navGame(idx) {
    if (idx < -1) idx = -1;
    if (idx >= pgnMoves.length) idx = pgnMoves.length - 1;
    pgnIndex = idx;

    game.reset();
    for (let i = 0; i <= idx; i++) game.move(pgnMoves[i].move_san);
    board.position(game.fen());
    currentFen = game.fen();

    $('.move-cell').removeClass('active');
    if (idx >= 0) {
        $(`.move-cell[data-idx="${idx}"]`).addClass('active');
        const m = pgnMoves[idx];
        // Use cached analysis if available
        if (gameAnalysisData[idx]) {
            showAnalysisResult(gameAnalysisData[idx]);
            if (gameAnalysisData[idx].explanation_fallback)
                $('#explanation').html(fmtExpl(gameAnalysisData[idx].explanation_fallback));
        } else {
            analyzeMove(m.move_uci, m.move_number, m.fen_before);
        }
    } else {
        showEmpty();
    }
    startAnalysis(currentFen);

    const el = $(`.move-cell[data-idx="${idx}"]`);
    if (el.length) el[0].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
}

// ===== Full Game Analysis + Coach =====
function analyzeFullGame() {
    if (!pgnMoves.length) return;
    const btn = $('#btn-analyze-game');
    btn.prop('disabled', true).text('Analyzing...');
    gameAnalysisData = {};

    // Show coach loading
    switchTab('coach');
    $('#coach-empty').hide();
    $('#coach-report').hide();
    $('#coach-loading').show();

    let done = 0;
    const total = pgnMoves.length;

    function analyzeNext(i) {
        if (i >= total) {
            btn.prop('disabled', false).text('Analyze Game');
            generateCoachReport();
            return;
        }
        const m = pgnMoves[i];
        $.post('/api/analyze_move', JSON.stringify({
            fen: m.fen_before, move: m.move_uci, move_number: m.move_number, player_rating: currentRating
        }), function (data) {
            if (!data.error) {
                gameAnalysisData[i] = data;
                $(`.move-cell[data-idx="${i}"]`).removeClass('best good inaccuracy mistake blunder').addClass(data.quality);
            }
            done++;
            const pct = Math.round((done / total) * 100);
            $('#coach-progress-fill').css('width', pct + '%');
            $('#coach-progress-label').text(`Analyzing move ${done} of ${total}...`);
            analyzeNext(i + 1);
        }, 'json').fail(() => { done++; analyzeNext(i + 1); });
    }

    analyzeNext(0);
}

function generateCoachReport() {
    $('#coach-loading').hide();

    // Determine player color (heuristic: the side with more moves, or default white)
    let playerColor = 'white';
    const whiteHeader = ($('#game-info').text().split(' vs ')[0] || '').trim();

    // Tally stats for the player's moves
    const stats = { best: 0, good: 0, inaccuracy: 0, mistake: 0, blunder: 0 };
    const keyMoments = [];
    let totalMoves = 0;

    pgnMoves.forEach((m, i) => {
        const d = gameAnalysisData[i];
        if (!d) return;
        // Analyze both sides
        if (d.quality) stats[d.quality] = (stats[d.quality] || 0) + 1;
        totalMoves++;

        if (d.quality === 'inaccuracy' || d.quality === 'mistake' || d.quality === 'blunder') {
            const moment = {
                index: i,
                moveNumber: m.move_number,
                side: m.side,
                played: d.move_san,
                quality: d.quality,
                cpLoss: d.cp_loss,
                bestMove: d.best_move_san,
                bestFindable: d.is_findable !== false,
                findabilityScore: d.findability_score,
                suggestion: '',
                findableAlt: null,
            };

            // Build suggestion
            if (d.quality === 'blunder') {
                moment.suggestion = `${d.move_san} loses ${(d.cp_loss / 100).toFixed(1)} pawns worth of advantage.`;
            } else if (d.quality === 'mistake') {
                moment.suggestion = `${d.move_san} is a mistake, costing ${(d.cp_loss / 100).toFixed(1)} pawns.`;
            } else {
                moment.suggestion = `${d.move_san} is slightly inaccurate.`;
            }

            // Check if best move is findable
            if (d.best_findability_score != null && d.best_findability_score >= 0.5) {
                moment.suggestion += ` ${d.best_move_san} was the better choice and quite findable.`;
            } else if (d.best_move_san) {
                moment.suggestion += ` The engine prefers ${d.best_move_san}, but it's hard to find in practice.`;
                // Look for findable alternative in top lines
                if (d.top_lines) {
                    // The findable alternative would need to come from the coach_report endpoint
                    // For now, suggest the best move anyway
                }
            }

            keyMoments.push(moment);
        }
    });

    // Accuracy
    const accuracy = totalMoves > 0 ? Math.round(((stats.best + stats.good) / totalMoves) * 100) : 0;

    // Render
    $('#accuracy-pct').text(accuracy + '%');
    const circumference = 2 * Math.PI * 42;
    const offset = circumference - (accuracy / 100) * circumference;
    $('#ring-fg').css('stroke-dashoffset', offset);
    if (accuracy >= 70) $('#ring-fg').css('stroke', 'var(--green)');
    else if (accuracy >= 50) $('#ring-fg').css('stroke', 'var(--orange)');
    else $('#ring-fg').css('stroke', 'var(--red)');

    $('#stat-best').text(stats.best);
    $('#stat-good').text(stats.good);
    $('#stat-inaccuracy').text(stats.inaccuracy);
    $('#stat-mistake').text(stats.mistake);
    $('#stat-blunder').text(stats.blunder);

    // Key moments
    const mc = $('#coach-moments').empty();
    if (keyMoments.length === 0) {
        mc.append('<div class="empty-state" style="padding:20px"><p>No significant mistakes found!</p></div>');
    } else {
        mc.append('<div style="margin-bottom:8px"><span class="section-label">Key Moments</span></div>');
        keyMoments.forEach(m => {
            const moveLabel = m.side === 'white' ? `${m.moveNumber}. ${m.played}` : `${m.moveNumber}... ${m.played}`;
            const altHtml = m.bestMove ? `<div class="moment-alt">💡 Better: <strong>${m.bestMove}</strong></div>` : '';
            mc.append(`<div class="moment-card ${m.quality}">
                <div class="moment-header">
                    <span class="moment-move">${moveLabel}</span>
                    <span class="moment-quality ${m.quality}">${m.quality}</span>
                </div>
                <div class="moment-body">${m.suggestion}</div>
                ${altHtml}
                <div class="moment-click" data-idx="${m.index}">Click to view position →</div>
            </div>`);
        });
        mc.find('.moment-click').click(function () {
            switchTab('analysis');
            navGame(+$(this).data('idx'));
        });
    }

    // Patterns
    const pc = $('#coach-patterns').empty();
    const patterns = [];
    if (stats.best + stats.good >= totalMoves * 0.7) patterns.push({ text: 'Strong overall accuracy', type: 'strength' });
    if (stats.blunder === 0) patterns.push({ text: 'No blunders — good discipline', type: 'strength' });
    if (stats.blunder >= 2) patterns.push({ text: `${stats.blunder} blunders — slow down and double-check`, type: 'weakness' });
    if (stats.mistake >= 3) patterns.push({ text: `${stats.mistake} mistakes — consider each move carefully`, type: 'weakness' });

    if (patterns.length) {
        pc.append('<div style="margin-bottom:8px;margin-top:8px"><span class="section-label">Patterns</span></div>');
        patterns.forEach(p => {
            const icon = p.type === 'strength' ? '✓' : '△';
            pc.append(`<div class="pattern-tag ${p.type}"><span class="pattern-icon">${icon}</span>${p.text}</div>`);
        });
    }

    $('#coach-report').show();
}

// ===== Helpers =====
function fmtEval(cp, mate) {
    if (mate != null) return (mate > 0 ? '+' : '') + 'M' + Math.abs(mate);
    if (cp == null) return '0.0';
    return (cp >= 0 ? '+' : '') + (cp / 100).toFixed(1);
}

function evalCls(cp) {
    if (cp > 50) return 'positive';
    if (cp < -50) return 'negative';
    return 'neutral';
}

function getFenBefore() {
    const t = new Chess();
    for (let i = 0; i < moveHistory.length - 1; i++) t.move(moveHistory[i]);
    return t.fen();
}

function setStatus(t) { $('#status-text').text(t); }

function showEmpty() {
    $('#analysis-loading').hide();
    $('#analysis-content').hide();
    $('#analysis-empty').show();
}

function switchTab(name) {
    $('.tab').removeClass('active');
    $(`[data-tab="${name}"]`).addClass('active');
    $('.tab-content').removeClass('active');
    $(`#panel-${name}`).addClass('active');
}

function playUci(uci) {
    const from = uci.substring(0, 2), to = uci.substring(2, 4), promo = uci[4];
    const m = game.move({ from, to, promotion: promo });
    if (m) { board.position(game.fen()); onMoveMade(m); }
}

function flipBoard() {
    board.flip();
    isFlipped = !isFlipped;
    // Swap player names
    const top = $('#player-top-name').text();
    const bot = $('#player-bottom-name').text();
    $('#player-top-name').text(bot);
    $('#player-bottom-name').text(top);
}

function resetBoard() {
    game.reset();
    board.start();
    currentFen = game.fen();
    moveHistory = [];
    pgnMoves = [];
    pgnIndex = -1;
    gameAnalysisData = {};
    $('#move-list').empty();
    $('#movelist-area').removeClass('active');
    showEmpty();
    // Reset coach
    $('#coach-report').hide();
    $('#coach-loading').hide();
    $('#coach-empty').show();
    startAnalysis(currentFen);
}

function undoMove() {
    if (!moveHistory.length) return;
    game.undo();
    moveHistory.pop();
    currentFen = game.fen();
    board.position(currentFen);
    showEmpty();
    startAnalysis(currentFen);
}

function updateConfig() {
    $.post('/api/set_config', JSON.stringify({ skill_level: currentSkillLevel, player_rating: currentRating }),
        () => startAnalysis(currentFen), 'json');
}

function setSkillLevel(level) {
    currentSkillLevel = level;
    $('.skill-toggle button').removeClass('active');
    $(`#btn-${level}`).addClass('active');
    updateConfig();
}

function toast(msg, type) {
    type = type || 'info';
    const el = $(`<div class="toast ${type}">${msg}</div>`);
    $('#toast-container').append(el);
    setTimeout(() => el.remove(), 3500);
}

// Set content type for all AJAX posts
$.ajaxSetup({
    contentType: 'application/json',
    processData: false,
});
