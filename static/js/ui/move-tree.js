/**
 * Move tree — tree data structure and rendering for variations.
 *
 * Supports:
 * - Main line display
 * - Branching variations when a different move is made from an existing position
 * - Navigation through the tree
 * - Quality annotations per node
 */

let treeId = 0;

/** A single node in the move tree. */
export class MoveNode {
    constructor(moveSan, moveUci, fen, fenBefore, parent = null) {
        this.id = ++treeId;
        this.moveSan = moveSan;
        this.moveUci = moveUci;
        this.fen = fen;           // position AFTER this move
        this.fenBefore = fenBefore; // position BEFORE this move
        this.parent = parent;
        this.children = [];       // MoveNode[]
        this.quality = null;      // best/good/inaccuracy/mistake/blunder
        this.moveNumber = 0;
        this.side = 'white';      // 'white' or 'black'
    }

    /** Check if this node is on the main line (first child at every level). */
    isMainLine() {
        let node = this;
        while (node.parent) {
            if (node.parent.children[0] !== node) return false;
            node = node.parent;
        }
        return true;
    }

    /** Add a child node. Returns the child. */
    addChild(node) {
        node.parent = this;
        this.children.push(node);
        return node;
    }

    /** Get main continuation (first child). */
    getMainContinuation() {
        return this.children[0] || null;
    }

    /** Get the main line from this node to the end. */
    getMainLine() {
        const line = [];
        let node = this.getMainContinuation();
        while (node) {
            line.push(node);
            node = node.getMainContinuation();
        }
        return line;
    }

    /** Get path from root to this node. */
    getPath() {
        const path = [];
        let node = this;
        while (node.parent) {
            path.unshift(node);
            node = node.parent;
        }
        return path;
    }
}

/** The move tree manages a rooted tree of moves. */
export class MoveTree {
    constructor() {
        this.root = new MoveNode(null, null, 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', null);
        this.currentNode = this.root;
    }

    /** Reset the tree to empty. */
    reset(startFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1') {
        treeId = 0;
        this.root = new MoveNode(null, null, startFen, null);
        this.currentNode = this.root;
    }

    /**
     * Add a move from the current position.
     * If the move already exists as a child, navigate to it.
     * If a different move exists, create a variation branch.
     * @returns {MoveNode} The node for the played move.
     */
    addMove(moveSan, moveUci, fenAfter) {
        // Check if this move already exists as a child
        for (const child of this.currentNode.children) {
            if (child.moveUci === moveUci || child.moveSan === moveSan) {
                this.currentNode = child;
                return child;
            }
        }

        // Determine move number and side
        const parentPath = this.currentNode.getPath();
        const plyCount = parentPath.length; // 0-based ply from root
        const moveNumber = Math.floor(plyCount / 2) + 1;
        const side = plyCount % 2 === 0 ? 'white' : 'black';

        const node = new MoveNode(moveSan, moveUci, fenAfter, this.currentNode.fen, this.currentNode);
        node.moveNumber = moveNumber;
        node.side = side;
        this.currentNode.addChild(node);
        this.currentNode = node;
        return node;
    }

    /** Navigate to a specific node. */
    goTo(node) {
        this.currentNode = node;
    }

    /** Go to root (start position). */
    goToStart() {
        this.currentNode = this.root;
    }

    /** Go forward along main continuation. */
    goForward() {
        const next = this.currentNode.getMainContinuation();
        if (next) {
            this.currentNode = next;
            return true;
        }
        return false;
    }

    /** Go backward to parent. */
    goBack() {
        if (this.currentNode.parent) {
            this.currentNode = this.currentNode.parent;
            return true;
        }
        return false;
    }

    /** Go to the last move on the main line. */
    goToEnd() {
        while (this.goForward()) {}
    }

    /** Get the main line moves as a flat array (for PGN display / game analysis). */
    getMainLineMoves() {
        return this.root.getMainLine();
    }

    /**
     * Load moves from a flat PGN move list.
     * @param {object[]} pgnMoves - [{moveSan, moveUci, fenBefore, moveNumber, side}]
     * @param {string} startFen
     */
    loadFromPgn(pgnMoves, startFen) {
        this.reset(startFen || 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1');

        for (const m of pgnMoves) {
            const node = new MoveNode(m.moveSan, m.moveUci, null, this.currentNode.fen, this.currentNode);
            node.moveNumber = m.moveNumber;
            node.side = m.side;
            this.currentNode.addChild(node);
            this.currentNode = node;
        }

        // Go back to start
        this.currentNode = this.root;
    }

    /** Find a node by its unique id. */
    findById(id) {
        return this._findByIdRecursive(this.root, id);
    }

    _findByIdRecursive(node, id) {
        if (node.id === id) return node;
        for (const child of node.children) {
            const found = this._findByIdRecursive(child, id);
            if (found) return found;
        }
        return null;
    }
}

// ===== Rendering =====

let moveTreeEl = null;
let onNavigateCallback = null;
let currentTree = null;

/**
 * Initialize the move tree renderer.
 * @param {HTMLElement} el - Container element
 * @param {function} navCallback - called with (MoveNode) on click
 */
export function initMoveTreeUI(el, navCallback) {
    moveTreeEl = el;
    onNavigateCallback = navCallback;
}

/**
 * Render a move tree into the container.
 * @param {MoveTree} tree
 */
export function renderTree(tree) {
    currentTree = tree;
    if (!moveTreeEl) return;
    moveTreeEl.innerHTML = '';
    renderNode(moveTreeEl, tree.root, true);
    highlightCurrentNode(tree);
}

/**
 * Highlight the current node in the tree.
 * @param {MoveTree} tree
 */
export function highlightCurrentNode(tree) {
    if (!moveTreeEl) return;
    moveTreeEl.querySelectorAll('.move-cell').forEach(el => {
        el.classList.toggle('active', parseInt(el.dataset.nodeId) === tree.currentNode.id);
    });

    // Scroll into view
    const active = moveTreeEl.querySelector('.move-cell.active');
    if (active) active.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
}

/**
 * Update quality class on a specific node.
 * @param {number} nodeId
 * @param {string} quality
 */
export function setNodeQuality(nodeId, quality) {
    const cell = moveTreeEl?.querySelector(`[data-node-id="${nodeId}"]`);
    if (cell) {
        cell.classList.remove('best', 'good', 'inaccuracy', 'mistake', 'blunder');
        if (quality) cell.classList.add(quality);
    }
}

// ===== Internal rendering =====

function renderNode(container, node, isMainLine) {
    // Render children
    for (let i = 0; i < node.children.length; i++) {
        const child = node.children[i];

        if (i === 0) {
            // Main continuation — render inline
            renderMoveCell(container, child);

            // If there are variations (siblings), render them
            for (let j = 1; j < node.children.length; j++) {
                renderVariation(container, node.children[j]);
            }

            // Continue main line
            renderNode(container, child, isMainLine);
        }
        // Variations handled above when i === 0
        break; // Only process first child in the loop, variations handled inline
    }
}

function renderMoveCell(container, node) {
    // Add move number if white's move or first move in a variation
    if (node.side === 'white') {
        const numSpan = document.createElement('span');
        numSpan.className = 'move-num';
        numSpan.textContent = node.moveNumber + '.';
        container.appendChild(numSpan);
    }

    const cell = document.createElement('span');
    cell.className = 'move-cell';
    if (node.quality) cell.classList.add(node.quality);
    cell.dataset.nodeId = node.id;
    cell.textContent = node.moveSan;
    cell.addEventListener('click', () => {
        if (onNavigateCallback) onNavigateCallback(node);
    });
    container.appendChild(cell);
}

function renderVariation(container, node) {
    const varLine = document.createElement('div');
    varLine.className = 'variation-line';

    // Add move number with ellipsis for black
    if (node.side === 'white') {
        const numSpan = document.createElement('span');
        numSpan.className = 'move-num';
        numSpan.textContent = node.moveNumber + '.';
        varLine.appendChild(numSpan);
    } else {
        const numSpan = document.createElement('span');
        numSpan.className = 'move-num';
        numSpan.textContent = node.moveNumber + '...';
        varLine.appendChild(numSpan);
    }

    renderMoveCell(varLine, node);

    // Render the rest of this variation's main line
    renderNode(varLine, node, false);

    container.appendChild(varLine);
}
