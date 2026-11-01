/**
 * NexusContacts — Minimalist Frontend Application Logic
 * ====================================================
 * Connects modern UI events with FastAPI REST endpoints and synchronizes
 * in-memory ADSA structures.
 */

const API_BASE = '/api';

// Application State
const state = {
  contacts: [],
  selectedCategory: 'All',
  sortBy: 'alphabetical',
  searchQuery: '',
  searchMode: 'autocomplete', // 'autocomplete' | 'fuzzy' | 'linear'
  viewMode: 'grid',           // 'grid' | 'list'
  adsaStats: null,
  activeContact: null
};

// DOM Elements
const elements = {
  contactsGrid: document.getElementById('contacts-grid'),
  totalContactsCount: document.getElementById('stat-total-contacts'),
  heapRootContact: document.getElementById('stat-top-contact'),
  avlHeightBadge: document.getElementById('stat-avl-height'),
  trieWordsCount: document.getElementById('stat-trie-words'),
  searchInput: document.getElementById('search-input'),
  searchModeSelect: document.getElementById('search-mode-select'),
  autocompleteDropdown: document.getElementById('autocomplete-dropdown'),
  sortSelect: document.getElementById('sort-select'),
  categoryTabs: document.querySelectorAll('.cat-tab'),
  frequentList: document.getElementById('frequent-list'),
  btnViewGrid: document.getElementById('btn-view-grid'),
  btnViewList: document.getElementById('btn-view-list'),
  btnResetData: document.getElementById('btn-reset-data'),
  contactModal: document.getElementById('contact-modal'),
  contactForm: document.getElementById('contact-form'),
  modalTitle: document.getElementById('modal-title'),
  btnOpenAddModal: document.getElementById('btn-open-add-modal'),
  btnCloseModal: document.getElementById('btn-close-modal'),
  btnCancelModal: document.getElementById('btn-cancel-modal'),
  adsaModal: document.getElementById('adsa-modal'),
  btnOpenAdsaModal: document.getElementById('btn-open-adsa-modal'),
  btnCloseAdsaModal: document.getElementById('btn-close-adsa-modal'),
  btnRefreshAdsa: document.getElementById('btn-refresh-adsa'),
  contactDrawer: document.getElementById('contact-drawer'),
  btnCloseDrawer: document.getElementById('btn-close-drawer'),
  themeToggle: document.getElementById('btn-theme-toggle'),
  toastContainer: document.getElementById('toast-container'),
  // Benchmark widget
  benchTrieUs: document.getElementById('bench-trie-us'),
  benchLinearUs: document.getElementById('bench-linear-us'),
  benchSpeedup: document.getElementById('bench-speedup'),
  benchBarTrie: document.getElementById('bench-bar-trie'),
  benchBarLinear: document.getElementById('bench-bar-linear'),
  // Inspector Tabs
  inspectorTabs: document.querySelectorAll('.tab-link'),
  tabContents: document.querySelectorAll('.tab-pane'),
  // BFS path inputs
  bfsFromSelect: document.getElementById('bfs-from-select'),
  bfsToSelect: document.getElementById('bfs-to-select'),
  btnFindBfsPath: document.getElementById('btn-find-bfs-path'),
  bfsResultContainer: document.getElementById('bfs-result-container'),
  // Levenshtein tester
  levWord1: document.getElementById('lev-word1'),
  levWord2: document.getElementById('lev-word2'),
  btnRunLevenshtein: document.getElementById('btn-run-levenshtein'),
  levTableContainer: document.getElementById('lev-table-container'),
  levDistanceBadge: document.getElementById('lev-distance-badge')
};

// =========================================================================
// Initialization
// =========================================================================

document.addEventListener('DOMContentLoaded', () => {
  // Initialize canvas visualizers
  if (window.adsaVisualizer) {
    window.adsaVisualizer.init('avl-canvas', 'graph-canvas');
  }

  setupEventListeners();

  // Load initial data
  loadContacts();
  loadFrequentContacts();
  loadADSAStats();
  runBenchmark('a');
});

function setupEventListeners() {
  // Category Tabs
  elements.categoryTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      elements.categoryTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      state.selectedCategory = tab.dataset.category;
      loadContacts();
    });
  });

  // Sort Selector
  if (elements.sortSelect) {
    elements.sortSelect.addEventListener('change', (e) => {
      state.sortBy = e.target.value;
      loadContacts();
    });
  }

  // View Mode Switcher (Grid vs List)
  if (elements.btnViewGrid) {
    elements.btnViewGrid.addEventListener('click', () => {
      state.viewMode = 'grid';
      elements.btnViewGrid.classList.add('active');
      elements.btnViewList.classList.remove('active');
      elements.contactsGrid.className = 'contacts-wrapper view-grid';
      renderContacts(state.contacts);
    });
  }
  if (elements.btnViewList) {
    elements.btnViewList.addEventListener('click', () => {
      state.viewMode = 'list';
      elements.btnViewList.classList.add('active');
      elements.btnViewGrid.classList.remove('active');
      elements.contactsGrid.className = 'contacts-wrapper view-list';
      renderContacts(state.contacts);
    });
  }

  // Search Input with Debounce & Autocomplete
  let searchTimeout = null;
  if (elements.searchInput) {
    elements.searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      const query = e.target.value.trim();
      state.searchQuery = query;

      if (!query) {
        hideAutocomplete();
        loadContacts();
        return;
      }

      searchTimeout = setTimeout(() => {
        handleSearch(query);
      }, 140);
    });

    // Close autocomplete on click outside
    document.addEventListener('click', (e) => {
      if (!elements.searchInput.contains(e.target) && !elements.autocompleteDropdown.contains(e.target)) {
        hideAutocomplete();
      }
    });

    // Keyboard shortcut (⌘K or / to focus search)
    window.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        elements.searchInput.focus();
      } else if (e.key === '/' && document.activeElement !== elements.searchInput && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
        e.preventDefault();
        elements.searchInput.focus();
      }
    });
  }

  // Search Mode Change
  if (elements.searchModeSelect) {
    elements.searchModeSelect.addEventListener('change', (e) => {
      state.searchMode = e.target.value;
      if (state.searchQuery) {
        handleSearch(state.searchQuery);
      }
    });
  }

  // Reset Demo Data Button
  if (elements.btnResetData) {
    elements.btnResetData.addEventListener('click', handleResetDemoData);
  }

  // Modal Triggers
  if (elements.btnOpenAddModal) {
    elements.btnOpenAddModal.addEventListener('click', () => openContactModal());
  }
  if (elements.btnCloseModal) {
    elements.btnCloseModal.addEventListener('click', closeContactModal);
  }
  if (elements.btnCancelModal) {
    elements.btnCancelModal.addEventListener('click', closeContactModal);
  }

  // Contact Form Submit
  if (elements.contactForm) {
    elements.contactForm.addEventListener('submit', handleFormSubmit);
  }

  // ADSA Inspector Modal
  if (elements.btnOpenAdsaModal) {
    elements.btnOpenAdsaModal.addEventListener('click', openAdsaInspector);
  }
  if (elements.btnCloseAdsaModal) {
    elements.btnCloseAdsaModal.addEventListener('click', closeAdsaInspector);
  }
  if (elements.btnRefreshAdsa) {
    elements.btnRefreshAdsa.addEventListener('click', () => {
      loadADSAStats();
      refreshInspectorActiveTab();
      showToast('ADSA data structures refreshed', 'info');
    });
  }

  // Inspector Tabs
  elements.inspectorTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      elements.inspectorTabs.forEach(t => t.classList.remove('active'));
      elements.tabContents.forEach(c => c.classList.remove('active'));

      tab.classList.add('active');
      const targetId = tab.dataset.tab;
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add('active');
        refreshInspectorActiveTab(targetId);
      }
    });
  });

  // BFS Path Finder
  if (elements.btnFindBfsPath) {
    elements.btnFindBfsPath.addEventListener('click', handleFindBfsPath);
  }

  // Levenshtein Tester
  if (elements.btnRunLevenshtein) {
    elements.btnRunLevenshtein.addEventListener('click', handleRunLevenshtein);
  }

  // Theme Toggle
  if (elements.themeToggle) {
    elements.themeToggle.addEventListener('click', toggleTheme);
  }

  // Close Drawer
  if (elements.btnCloseDrawer) {
    elements.btnCloseDrawer.addEventListener('click', () => {
      elements.contactDrawer.classList.remove('active');
    });
  }
}

// =========================================================================
// API Calls & Data Fetching
// =========================================================================

async function loadContacts() {
  try {
    const params = new URLSearchParams({
      category: state.selectedCategory,
      sort_by: state.sortBy
    });

    if (state.searchQuery && state.searchMode !== 'autocomplete') {
      params.append('search', state.searchQuery);
    }

    const res = await fetch(`${API_BASE}/contacts?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch contacts');
    const contacts = await res.json();
    state.contacts = contacts;

    renderContacts(contacts);
    updateQuickStats();
  } catch (err) {
    console.error(err);
    showToast('Failed to load contacts', 'error');
  }
}

async function loadFrequentContacts() {
  try {
    const res = await fetch(`${API_BASE}/frequent?limit=5`);
    if (!res.ok) return;
    const items = await res.json();
    renderFrequentList(items);

    if (items.length > 0 && elements.heapRootContact) {
      elements.heapRootContact.textContent = items[0].name;
    }
  } catch (err) {
    console.error('Failed to load frequent contacts:', err);
  }
}

async function loadADSAStats() {
  try {
    const res = await fetch(`${API_BASE}/adsa/stats`);
    if (!res.ok) return;
    const stats = await res.json();
    state.adsaStats = stats;

    if (elements.totalContactsCount) elements.totalContactsCount.textContent = stats.total_contacts;
    if (elements.avlHeightBadge) elements.avlHeightBadge.innerHTML = `${stats.avl_tree.height} <span class="tag-balanced">Balanced</span>`;
    if (elements.trieWordsCount) elements.trieWordsCount.textContent = stats.trie.total_words_indexed;

    renderHashTableStats(stats.hash_table);
  } catch (err) {
    console.error('Failed to load ADSA stats:', err);
  }
}

async function runBenchmark(query) {
  try {
    const res = await fetch(`${API_BASE}/adsa/benchmark?q=${encodeURIComponent(query || 'a')}`);
    if (!res.ok) return;
    const data = await res.json();

    if (elements.benchTrieUs) elements.benchTrieUs.textContent = `${data.trie_time_us} μs`;
    if (elements.benchLinearUs) elements.benchLinearUs.textContent = `${data.linear_time_us} μs`;
    if (elements.benchSpeedup) elements.benchSpeedup.textContent = `${data.speedup_factor}x faster`;

    if (elements.benchBarTrie && elements.benchBarLinear) {
      const maxVal = Math.max(data.trie_time_us, data.linear_time_us, 1);
      const trieWidth = Math.max(12, Math.min(100, (data.trie_time_us / maxVal) * 100));
      const linearWidth = Math.max(15, Math.min(100, (data.linear_time_us / maxVal) * 100));
      elements.benchBarTrie.style.width = `${trieWidth}%`;
      elements.benchBarLinear.style.width = `${linearWidth}%`;
    }
  } catch (err) {
    console.error('Benchmark failed:', err);
  }
}

async function handleResetDemoData() {
  try {
    const res = await fetch(`${API_BASE}/reset-sample-data`, { method: 'POST' });
    if (!res.ok) throw new Error('Reset failed');
    const data = await res.json();

    showToast(`Sample dataset restored: ${data.total_contacts} contacts loaded`, 'success');
    loadContacts();
    loadFrequentContacts();
    loadADSAStats();
    runBenchmark('a');
  } catch (err) {
    showToast('Failed to reset demo data', 'error');
  }
}

// =========================================================================
// Search Handlers
// =========================================================================

async function handleSearch(query) {
  runBenchmark(query);

  if (state.searchMode === 'autocomplete') {
    try {
      const res = await fetch(`${API_BASE}/autocomplete?q=${encodeURIComponent(query)}`);
      const results = await res.json();
      showAutocompleteResults(results, query);

      const matchingContacts = results.map(r => r.contact);
      renderContacts(matchingContacts);
    } catch (err) {
      console.error(err);
    }
  } else if (state.searchMode === 'fuzzy') {
    try {
      const res = await fetch(`${API_BASE}/fuzzy?q=${encodeURIComponent(query)}&max_distance=2`);
      const matches = await res.json();
      hideAutocomplete();
      renderContacts(matches.map(m => m.contact));
    } catch (err) {
      console.error(err);
    }
  } else {
    hideAutocomplete();
    loadContacts();
  }
}

function showAutocompleteResults(results, query) {
  if (!elements.autocompleteDropdown) return;

  if (results.length === 0) {
    elements.autocompleteDropdown.innerHTML = `
      <div class="autocomplete-header">
        <span>Trie Lookup: 0 matches</span>
      </div>
      <div style="padding: 0.65rem 0.85rem; color: var(--text-muted); font-size: 0.8rem;">
        No contact prefix starting with "<strong>${escapeHtml(query)}</strong>"
      </div>
    `;
    elements.autocompleteDropdown.classList.add('active');
    return;
  }

  let html = `
    <div class="autocomplete-header">
      <span>Trie Prefix Match (O(L+M))</span>
      <span>${results.length} results</span>
    </div>
  `;

  results.forEach(({ matched_prefix, contact }) => {
    html += `
      <div class="autocomplete-row" data-contact-id="${contact.id}">
        <div>
          <span class="autocomplete-name">${escapeHtml(contact.name)}</span>
          <span class="autocomplete-sub">[Prefix: ${escapeHtml(matched_prefix)}]</span>
        </div>
        <span class="font-mono text-muted" style="font-size: 0.75rem;">${escapeHtml(contact.phone)}</span>
      </div>
    `;
  });

  elements.autocompleteDropdown.innerHTML = html;
  elements.autocompleteDropdown.classList.add('active');

  elements.autocompleteDropdown.querySelectorAll('.autocomplete-row').forEach(row => {
    row.addEventListener('click', () => {
      const cid = parseInt(row.dataset.contactId);
      hideAutocomplete();
      openContactDrawer(cid);
    });
  });
}

function hideAutocomplete() {
  if (elements.autocompleteDropdown) {
    elements.autocompleteDropdown.classList.remove('active');
  }
}

// =========================================================================
// UI Rendering (Grid View & Compact List View)
// =========================================================================

function renderContacts(contacts) {
  if (!elements.contactsGrid) return;

  if (!contacts || contacts.length === 0) {
    elements.contactsGrid.innerHTML = `
      <div class="empty-state-minimal" style="grid-column: 1 / -1; width: 100%;">
        <h4>No contacts found</h4>
        <p>${state.searchQuery ? `No matching records for "${escapeHtml(state.searchQuery)}".` : 'Add your first contact or click Reset Demo to load sample data.'}</p>
        <button class="btn btn-primary" onclick="handleResetDemoData()">Restore Sample Contacts</button>
      </div>
    `;
    return;
  }

  if (state.viewMode === 'list') {
    renderListView(contacts);
  } else {
    renderGridView(contacts);
  }
}

function renderGridView(contacts) {
  elements.contactsGrid.innerHTML = contacts.map(c => `
    <div class="contact-card-minimal" data-id="${c.id}">
      <div>
        <div class="card-header-line">
          <div class="identity-cluster">
            <div class="avatar-disc">${getInitials(c.name)}</div>
            <div class="identity-text">
              <h4 onclick="openContactDrawer(${c.id})">${escapeHtml(c.name)}</h4>
              <span class="category-pill-minimal cat-${(c.category || 'general').toLowerCase()}">${escapeHtml(c.category || 'General')}</span>
            </div>
          </div>
          <button class="star-toggle-btn ${c.is_favorite ? 'starred' : ''}" onclick="toggleFavorite(${c.id}, event)" title="${c.is_favorite ? 'Starred' : 'Star Contact'}">
            ★
          </button>
        </div>

        <div class="contact-meta-fields">
          <div class="meta-field">
            <span class="meta-icon">📞</span>
            <span class="font-mono">${escapeHtml(c.phone)}</span>
          </div>
          ${c.email ? `
            <div class="meta-field">
              <span class="meta-icon">✉️</span>
              <span>${escapeHtml(c.email)}</span>
            </div>
          ` : ''}
          ${c.company ? `
            <div class="meta-field">
              <span class="meta-icon">💼</span>
              <span>${escapeHtml(c.company)}</span>
            </div>
          ` : ''}
        </div>
      </div>

      <div class="card-action-bar">
        <div class="interaction-tag" title="Interactions recorded by Max-Heap Priority Queue">
          ⚡ <span>${c.call_count || 0}</span> calls
        </div>
        <div class="action-buttons-group">
          <button class="micro-btn btn-call" onclick="recordCall(${c.id}, event)" title="Simulate Call (+1 Heap Interaction)">
            📞
          </button>
          <button class="micro-btn" onclick="editContact(${c.id}, event)" title="Edit Contact">
            ✏️
          </button>
          <button class="micro-btn btn-del" onclick="deleteContact(${c.id}, event)" title="Delete Contact">
            ✕
          </button>
        </div>
      </div>
    </div>
  `).join('');
}

function renderListView(contacts) {
  elements.contactsGrid.innerHTML = contacts.map(c => `
    <div class="contact-row-minimal" data-id="${c.id}">
      <div class="row-col-name">
        <div class="avatar-disc avatar-disc-sm">${getInitials(c.name)}</div>
        <span style="font-weight: 600; color: var(--text-main); cursor: pointer;" onclick="openContactDrawer(${c.id})">${escapeHtml(c.name)}</span>
      </div>
      <div class="row-col-category">
        <span class="category-pill-minimal cat-${(c.category || 'general').toLowerCase()}">${escapeHtml(c.category || 'General')}</span>
      </div>
      <div class="row-col-phone">${escapeHtml(c.phone)}</div>
      <div class="row-col-email">${escapeHtml(c.email || '—')}</div>
      <div class="font-mono text-muted" style="font-size: 0.75rem; min-width: 60px;">⚡ ${c.call_count || 0}</div>
      <div class="row-col-actions">
        <button class="star-toggle-btn ${c.is_favorite ? 'starred' : ''}" onclick="toggleFavorite(${c.id}, event)" style="font-size: 0.95rem;">★</button>
        <button class="micro-btn btn-call" onclick="recordCall(${c.id}, event)" title="Call">📞</button>
        <button class="micro-btn" onclick="editContact(${c.id}, event)" title="Edit">✏️</button>
        <button class="micro-btn btn-del" onclick="deleteContact(${c.id}, event)" title="Delete">✕</button>
      </div>
    </div>
  `).join('');
}

function renderFrequentList(items) {
  if (!elements.frequentList) return;

  if (!items || items.length === 0) {
    elements.frequentList.innerHTML = '<p style="color: var(--text-muted); font-size: 0.75rem;">No interaction data yet.</p>';
    return;
  }

  elements.frequentList.innerHTML = items.map((c, i) => `
    <div class="frequent-item" onclick="openContactDrawer(${c.id})">
      <div style="display: flex; align-items: center; gap: 0.5rem;">
        <span class="frequent-rank">#${i + 1}</span>
        <span class="frequent-name">${escapeHtml(c.name)}</span>
      </div>
      <span class="frequent-score">${c.call_count} calls</span>
    </div>
  `).join('');
}

function updateQuickStats() {
  if (state.contacts && elements.totalContactsCount) {
    elements.totalContactsCount.textContent = state.contacts.length;
  }
}

// =========================================================================
// Contact Actions & Form Handling
// =========================================================================

async function recordCall(contactId, event) {
  if (event) event.stopPropagation();
  try {
    const res = await fetch(`${API_BASE}/contacts/${contactId}/call`, { method: 'POST' });
    if (!res.ok) throw new Error('Call recording failed');
    const data = await res.json();

    showToast(`Call logged with ${data.contact.name}. Heap re-ranked!`, 'success');
    loadContacts();
    loadFrequentContacts();
  } catch (err) {
    showToast('Failed to record call', 'error');
  }
}

async function toggleFavorite(contactId, event) {
  if (event) event.stopPropagation();
  const contact = state.contacts.find(c => c.id === contactId);
  if (!contact) return;

  const newFavStatus = !contact.is_favorite;
  try {
    const res = await fetch(`${API_BASE}/contacts/${contactId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_favorite: newFavStatus })
    });
    if (!res.ok) throw new Error('Favorite update failed');

    showToast(newFavStatus ? 'Starred contact (+100 heap bonus)' : 'Unstarred contact', 'info');
    loadContacts();
    loadFrequentContacts();
  } catch (err) {
    showToast('Failed to update favorite', 'error');
  }
}

async function deleteContact(contactId, event) {
  if (event) event.stopPropagation();
  const contact = state.contacts.find(c => c.id === contactId);
  const name = contact ? contact.name : 'this contact';

  if (!confirm(`Delete ${name}? This removes it from SQLite, Trie, and AVL Tree.`)) {
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/contacts/${contactId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Delete failed');

    showToast(`Deleted ${name}`, 'info');
    loadContacts();
    loadFrequentContacts();
    loadADSAStats();
  } catch (err) {
    showToast('Failed to delete contact', 'error');
  }
}

function openContactModal(contact = null) {
  state.activeContact = contact;
  elements.modalTitle.textContent = contact ? 'Edit Contact' : 'New Contact';

  document.getElementById('form-name').value = contact ? contact.name : '';
  document.getElementById('form-phone').value = contact ? contact.phone : '';
  document.getElementById('form-email').value = contact ? contact.email : '';
  document.getElementById('form-category').value = contact ? contact.category : 'College';
  document.getElementById('form-company').value = contact ? contact.company : '';
  document.getElementById('form-notes').value = contact ? contact.notes : '';
  document.getElementById('form-favorite').checked = contact ? contact.is_favorite : false;

  elements.contactModal.classList.add('active');
}

function closeContactModal() {
  elements.contactModal.classList.remove('active');
  state.activeContact = null;
  elements.contactForm.reset();
}

function editContact(contactId, event) {
  if (event) event.stopPropagation();
  const contact = state.contacts.find(c => c.id === contactId);
  if (contact) {
    openContactModal(contact);
  }
}

async function handleFormSubmit(e) {
  e.preventDefault();

  const payload = {
    name: document.getElementById('form-name').value.trim(),
    phone: document.getElementById('form-phone').value.trim(),
    email: document.getElementById('form-email').value.trim() || null,
    category: document.getElementById('form-category').value,
    company: document.getElementById('form-company').value.trim() || '',
    notes: document.getElementById('form-notes').value.trim() || '',
    is_favorite: document.getElementById('form-favorite').checked
  };

  try {
    let res;
    if (state.activeContact) {
      res = await fetch(`${API_BASE}/contacts/${state.activeContact.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch(`${API_BASE}/contacts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    }

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Save failed');

    showToast(state.activeContact ? 'Contact updated in ADSA memory' : 'Contact added to Trie & AVL Tree', 'success');
    closeContactModal();
    loadContacts();
    loadFrequentContacts();
    loadADSAStats();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// =========================================================================
// Contact Drawer
// =========================================================================

async function openContactDrawer(contactId) {
  try {
    const res = await fetch(`${API_BASE}/contacts/${contactId}`);
    if (!res.ok) return;
    const c = await res.json();

    document.getElementById('drawer-avatar').textContent = getInitials(c.name);
    document.getElementById('drawer-name').textContent = c.name;
    document.getElementById('drawer-category').textContent = c.category;
    document.getElementById('drawer-category').className = `category-pill-minimal cat-${(c.category || 'general').toLowerCase()}`;
    document.getElementById('drawer-phone').textContent = c.phone;
    document.getElementById('drawer-email').textContent = c.email || 'None';
    document.getElementById('drawer-company').textContent = c.company || 'Not specified';
    document.getElementById('drawer-notes').textContent = c.notes || 'No notes added.';
    document.getElementById('drawer-call-count').textContent = `${c.call_count} calls`;

    elements.contactDrawer.classList.add('active');
  } catch (err) {
    console.error(err);
  }
}

// =========================================================================
// ADSA Inspector
// =========================================================================

async function openAdsaInspector() {
  elements.adsaModal.classList.add('active');
  await loadADSAStats();
  populateBfsContactSelects();
  refreshInspectorActiveTab();
}

function closeAdsaInspector() {
  elements.adsaModal.classList.remove('active');
}

async function refreshInspectorActiveTab(tabId = null) {
  const activeTab = tabId || document.querySelector('.inspector-tabs-bar .tab-link.active').dataset.tab;

  if (activeTab === 'tab-avl') {
    try {
      const res = await fetch(`${API_BASE}/avl/structure`);
      const data = await res.json();
      window.adsaVisualizer.renderAVLTree(data.tree);

      document.getElementById('avl-rotations-info').textContent = 
        `Rotations: LL: ${data.rotations.LL} | RR: ${data.rotations.RR} | LR: ${data.rotations.LR} | RL: ${data.rotations.RL} (Height: ${data.height})`;
    } catch (err) {
      console.error(err);
    }
  } else if (activeTab === 'tab-graph') {
    try {
      const res = await fetch(`${API_BASE}/graph`);
      const data = await res.json();
      window.adsaVisualizer.setNetworkData(data);
      window.adsaVisualizer.renderGraph();
    } catch (err) {
      console.error(err);
    }
  }
}

function populateBfsContactSelects() {
  if (!elements.bfsFromSelect || !elements.bfsToSelect) return;

  const options = state.contacts.map(c => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join('');
  elements.bfsFromSelect.innerHTML = options;
  elements.bfsToSelect.innerHTML = options;

  if (state.contacts.length >= 2) {
    elements.bfsToSelect.selectedIndex = 1;
  }
}

async function handleFindBfsPath() {
  const fromId = parseInt(elements.bfsFromSelect.value);
  const toId = parseInt(elements.bfsToSelect.value);

  if (fromId === toId) {
    showToast('Select two different contacts to find connections.', 'info');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/relationships/path?from_id=${fromId}&to_id=${toId}`);
    const data = await res.json();

    if (!data.connected) {
      elements.bfsResultContainer.innerHTML = `<span style="color: var(--accent-rose);">No connection path found.</span>`;
      window.adsaVisualizer.renderGraph([]);
      return;
    }

    const pathNodes = data.path.map(p => p.id);
    window.adsaVisualizer.renderGraph(pathNodes);

    let pathHtml = `<span style="color: #38bdf8; font-weight: 600;">Degrees: ${data.degrees} hop(s): </span>`;
    data.path.forEach((step, idx) => {
      pathHtml += `<span style="color: var(--text-main); font-weight: 600;">${escapeHtml(step.name)}</span>`;
      if (step.relation_to_next) {
        pathHtml += ` <span style="color: var(--text-muted); font-size: 0.75rem;">→ [${escapeHtml(step.relation_to_next)}] →</span> `;
      }
    });

    elements.bfsResultContainer.innerHTML = pathHtml;
  } catch (err) {
    console.error(err);
  }
}

function handleRunLevenshtein() {
  const w1 = (elements.levWord1.value || 'Smith').trim();
  const w2 = (elements.levWord2.value || 'Smyth').trim();

  const m = w1.length;
  const n = w2.length;
  const dp = Array.from({ length: m + 1 }, () => Array(n + 1).fill(0));

  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (w1[i - 1].toLowerCase() === w2[j - 1].toLowerCase()) {
        dp[i][j] = dp[i - 1][j - 1];
      } else {
        dp[i][j] = 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
      }
    }
  }

  const distance = dp[m][n];
  if (elements.levDistanceBadge) {
    elements.levDistanceBadge.textContent = `Edit Distance: ${distance}`;
  }

  window.adsaVisualizer.renderLevenshteinTable('lev-table-container', w1, w2, dp);
}

function renderHashTableStats(htStats) {
  const container = document.getElementById('ht-stats-container');
  if (!container || !htStats) return;

  container.innerHTML = `
    <div class="ht-stat-card">
      <div class="ht-stat-val">${htStats.capacity}</div>
      <div class="ht-stat-lbl">Bucket Capacity</div>
    </div>
    <div class="ht-stat-card">
      <div class="ht-stat-val">${htStats.total_items}</div>
      <div class="ht-stat-lbl">Stored Keys</div>
    </div>
    <div class="ht-stat-card">
      <div class="ht-stat-val" style="color: ${htStats.load_factor > 0.75 ? '#f43f5e' : '#34d399'};">
        λ = ${htStats.load_factor}
      </div>
      <div class="ht-stat-lbl">Load Factor (Max 0.75)</div>
    </div>
    <div class="ht-stat-card">
      <div class="ht-stat-val">${htStats.total_collisions}</div>
      <div class="ht-stat-lbl">Collisions Handled</div>
    </div>
  `;
}

// =========================================================================
// Utilities
// =========================================================================

function showToast(message, type = 'info') {
  if (!elements.toastContainer) return;
  const toast = document.createElement('div');
  toast.className = `toast-capsule toast-${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
    <span>${escapeHtml(message)}</span>
  `;
  elements.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 250);
  }, 3000);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  if (elements.themeToggle) {
    const icon = elements.themeToggle.querySelector('.theme-icon');
    if (icon) icon.textContent = next === 'dark' ? '🌙' : '☀️';
  }
}

function getInitials(name) {
  if (!name) return 'C';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Expose globals for inline HTML event handlers
window.openContactModal = openContactModal;
window.editContact = editContact;
window.deleteContact = deleteContact;
window.recordCall = recordCall;
window.toggleFavorite = toggleFavorite;
window.openContactDrawer = openContactDrawer;
window.handleResetDemoData = handleResetDemoData;
