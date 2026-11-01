/**
 * ADSA Canvas Visualizer Engine
 * -----------------------------
 * 1. AVL Tree Visualizer (Hierarchical tree layout with balance factors)
 * 2. Contact Relationship Graph (Force-directed / radial node-edge rendering with BFS highlight)
 * 3. Levenshtein Dynamic Programming Grid Visualizer
 */

class ADSAVisualizer {
  constructor() {
    this.avlCanvas = null;
    this.avlCtx = null;
    this.graphCanvas = null;
    this.graphCtx = null;
    this.networkData = { nodes: [], edges: [] };
    this.activeBfsPath = [];
  }

  init(avlCanvasId, graphCanvasId) {
    this.avlCanvas = document.getElementById(avlCanvasId);
    if (this.avlCanvas) {
      this.avlCtx = this.avlCanvas.getContext('2d');
      this.resizeCanvas(this.avlCanvas);
    }

    this.graphCanvas = document.getElementById(graphCanvasId);
    if (this.graphCanvas) {
      this.graphCtx = this.graphCanvas.getContext('2d');
      this.resizeCanvas(this.graphCanvas);
    }

    window.addEventListener('resize', () => {
      if (this.avlCanvas) this.resizeCanvas(this.avlCanvas);
      if (this.graphCanvas) this.resizeCanvas(this.graphCanvas);
    });
  }

  resizeCanvas(canvas) {
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = (rect.width || 800) * dpr;
    canvas.height = (rect.height || 450) * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
  }

  // =========================================================================
  // 1. AVL TREE VISUALIZATION
  // =========================================================================

  renderAVLTree(treeData) {
    if (!this.avlCanvas || !this.avlCtx) return;
    const ctx = this.avlCtx;
    const rect = this.avlCanvas.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    ctx.clearRect(0, 0, width, height);

    if (!treeData) {
      ctx.fillStyle = '#64748b';
      ctx.font = '14px "Plus Jakarta Sans", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('AVL Tree is empty. Add contacts to view tree hierarchy.', width / 2, height / 2);
      return;
    }

    // Measure depth to scale vertical step
    const maxDepth = this._getTreeDepth(treeData);
    const verticalGap = Math.min(75, (height - 80) / Math.max(maxDepth, 1));
    const startY = 45;

    // Draw tree recursively
    this._drawAVLNode(ctx, treeData, width / 2, startY, width / 4, verticalGap, 1);
  }

  _getTreeDepth(node) {
    if (!node) return 0;
    return 1 + Math.max(this._getTreeDepth(node.left), this._getTreeDepth(node.right));
  }

  _drawAVLNode(ctx, node, x, y, horizontalGap, verticalGap, depth) {
    if (!node) return;

    const childY = y + verticalGap;
    const nextGap = Math.max(22, horizontalGap * 0.52);

    // Draw branch lines to children first
    if (node.left) {
      const childX = x - horizontalGap;
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(childX, childY);
      ctx.strokeStyle = 'rgba(99, 102, 241, 0.4)';
      ctx.lineWidth = 2;
      ctx.stroke();
      this._drawAVLNode(ctx, node.left, childX, childY, nextGap, verticalGap, depth + 1);
    }

    if (node.right) {
      const childX = x + horizontalGap;
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(childX, childY);
      ctx.strokeStyle = 'rgba(99, 102, 241, 0.4)';
      ctx.lineWidth = 2;
      ctx.stroke();
      this._drawAVLNode(ctx, node.right, childX, childY, nextGap, verticalGap, depth + 1);
    }

    // Node Circle
    const radius = 20;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);

    // Color code balance factor
    const bf = node.balance_factor;
    let fillColor = '#1e1b4b'; // Deep Indigo
    let strokeColor = '#818cf8';

    if (bf === 0) {
      strokeColor = '#34d399'; // Perfectly balanced (Green)
    } else if (Math.abs(bf) === 1) {
      strokeColor = '#fbbf24'; // Balanced (Amber)
    } else {
      strokeColor = '#f43f5e'; // Imbalance (Red)
    }

    ctx.fillStyle = fillColor;
    ctx.fill();
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // Node Key Label (First 6 chars of name)
    const displayName = (node.display || node.key).split(' ')[0].substring(0, 7);
    ctx.fillStyle = '#f8fafc';
    ctx.font = '600 10.5px "Plus Jakarta Sans", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(displayName, x, y - 2);

    // Balance Factor Badge (tiny pill above node)
    ctx.beginPath();
    ctx.arc(x + 14, y - 14, 8, 0, Math.PI * 2);
    ctx.fillStyle = strokeColor;
    ctx.fill();

    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 9px JetBrains Mono, monospace';
    ctx.fillText(bf > 0 ? `+${bf}` : `${bf}`, x + 14, y - 13);
  }

  // =========================================================================
  // 2. CONTACT RELATIONSHIP GRAPH (BFS PATH HIGHLIGHTING)
  // =========================================================================

  setNetworkData(data) {
    this.networkData = data || { nodes: [], edges: [] };
  }

  renderGraph(highlightedPathIds = []) {
    if (!this.graphCanvas || !this.graphCtx) return;
    const ctx = this.graphCtx;
    const rect = this.graphCanvas.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    ctx.clearRect(0, 0, width, height);

    const nodes = this.networkData.nodes || [];
    const edges = this.networkData.edges || [];

    if (nodes.length === 0) {
      ctx.fillStyle = '#64748b';
      ctx.font = '14px "Plus Jakarta Sans", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('No relationship data available.', width / 2, height / 2);
      return;
    }

    // Position nodes in an attractive radial/circular formation
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.38;
    const nodePositions = new Map();

    nodes.forEach((node, idx) => {
      const angle = (idx / nodes.length) * (Math.PI * 2) - Math.PI / 2;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      nodePositions.set(node.id, { x, y, node });
    });

    const pathSet = new Set(highlightedPathIds);

    // 1. Draw Edges
    edges.forEach(edge => {
      const u = nodePositions.get(edge.source);
      const v = nodePositions.get(edge.target);
      if (!u || !v) return;

      const isPathEdge = pathSet.has(edge.source) && pathSet.has(edge.target);

      ctx.beginPath();
      ctx.moveTo(u.x, u.y);
      ctx.lineTo(v.x, v.y);

      if (isPathEdge) {
        ctx.strokeStyle = '#38bdf8'; // Glowing Cyan for BFS shortest path
        ctx.lineWidth = 3.5;
        ctx.setLineDash([]);
      } else {
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
        ctx.lineWidth = 1.2;
        ctx.setLineDash([4, 4]);
      }
      ctx.stroke();
      ctx.setLineDash([]);

      // Draw relationship label along the edge midpoint
      if (isPathEdge || nodes.length <= 15) {
        const midX = (u.x + v.x) / 2;
        const midY = (u.y + v.y) / 2;
        ctx.fillStyle = isPathEdge ? '#38bdf8' : '#94a3b8';
        ctx.font = '500 9px "Plus Jakarta Sans", sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(edge.relation || 'Connected', midX, midY - 4);
      }
    });

    // 2. Draw Nodes
    nodePositions.forEach(({ x, y, node }) => {
      const isHighlighted = pathSet.has(node.id);
      const nodeRadius = isHighlighted ? 22 : 17;

      ctx.beginPath();
      ctx.arc(x, y, nodeRadius, 0, Math.PI * 2);
      ctx.fillStyle = isHighlighted ? '#0284c7' : '#1e293b';
      ctx.fill();

      ctx.strokeStyle = isHighlighted ? '#38bdf8' : 'rgba(99, 102, 241, 0.6)';
      ctx.lineWidth = isHighlighted ? 3 : 1.5;
      ctx.stroke();

      // Node Initials or Short Name
      const initials = (node.name || 'C')
        .split(' ')
        .map(w => w[0])
        .join('')
        .substring(0, 2)
        .toUpperCase();

      ctx.fillStyle = '#ffffff';
      ctx.font = `bold ${isHighlighted ? '11px' : '9.5px'} "Plus Jakarta Sans", sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(initials, x, y);

      // Node Full Name below circle
      ctx.fillStyle = isHighlighted ? '#38bdf8' : '#cbd5e1';
      ctx.font = `${isHighlighted ? '600' : '400'} 10px "Plus Jakarta Sans", sans-serif`;
      ctx.fillText(node.name.split(' ')[0], x, y + nodeRadius + 12);
    });
  }

  // =========================================================================
  // 3. LEVENSHTEIN DYNAMIC PROGRAMMING TABLE RENDERER
  // =========================================================================

  renderLevenshteinTable(containerId, word1, word2, dpMatrix) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!word1 || !word2 || !dpMatrix) {
      container.innerHTML = '<p class="text-muted">Enter two words to inspect the DP computation table.</p>';
      return;
    }

    let html = `
      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-family: var(--font-mono); font-size: 0.8rem; text-align: center;">
          <thead>
            <tr style="background: rgba(99, 102, 241, 0.15);">
              <th style="padding: 6px; border: 1px solid rgba(255,255,255,0.1);">DP</th>
              <th style="padding: 6px; border: 1px solid rgba(255,255,255,0.1);">ε</th>
    `;

    for (let c of word2) {
      html += `<th style="padding: 6px; border: 1px solid rgba(255,255,255,0.1); color: var(--accent-cyan);">${c}</th>`;
    }
    html += `</tr></thead><tbody>`;

    for (let i = 0; i <= word1.length; i++) {
      const rowChar = i === 0 ? 'ε' : word1[i - 1];
      html += `<tr><td style="padding: 6px; font-weight: bold; background: rgba(99, 102, 241, 0.15); color: var(--accent-primary); border: 1px solid rgba(255,255,255,0.1);">${rowChar}</td>`;
      for (let j = 0; j <= word2.length; j++) {
        const val = dpMatrix[i][j];
        const isFinal = (i === word1.length && j === word2.length);
        const cellStyle = isFinal
          ? 'background: rgba(16, 185, 129, 0.3); color: #34d399; font-weight: bold; border: 2px solid #34d399;'
          : 'border: 1px solid rgba(255,255,255,0.06); color: var(--text-secondary);';
        html += `<td style="padding: 6px; ${cellStyle}">${val}</td>`;
      }
      html += `</tr>`;
    }

    html += `</tbody></table></div>`;
    container.innerHTML = html;
  }
}

// Global visualizer instance
window.adsaVisualizer = new ADSAVisualizer();
