/**
 * shared.js — Common utilities for all AXIS dashboard pages.
 * No logic here touches backend Python or makes external API calls.
 */

// ─── Supabase client singleton ────────────────────────────────────────────────
let _supabase = null;

function getSupabase() {
    if (_supabase) return _supabase;
    const url = localStorage.getItem('SUPABASE_URL');
    const key = localStorage.getItem('SUPABASE_ANON_KEY');
    if (url && key) {
        _supabase = window.supabase.createClient(url, key);
    }
    return _supabase;
}

function setSupabase(client) { _supabase = client; }

// ─── Time helpers (IST-aware) ─────────────────────────────────────────────────
function formatTimeIST(isoString) {
    if (!isoString) return '--';
    return new Date(isoString).toLocaleTimeString('en-IN', {
        timeZone: 'Asia/Kolkata',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
}

function formatDateIST(isoString) {
    if (!isoString) return '--';
    return new Date(isoString).toLocaleDateString('en-IN', {
        timeZone: 'Asia/Kolkata',
        day: '2-digit', month: 'short', year: 'numeric'
    });
}

function timeAgoMinutes(isoString) {
    if (!isoString) return Infinity;
    return Math.floor((Date.now() - new Date(isoString)) / 60000);
}

function formatINR(val) {
    return '₹' + Number(val || 0).toLocaleString('en-IN');
}

// ─── PNL class helper ─────────────────────────────────────────────────────────
function pnlClass(val) {
    const n = Number(val || 0);
    if (n > 0) return 'pnl-positive';
    if (n < 0) return 'pnl-negative';
    return '';
}

// ─── Config modal (shared across pages) ──────────────────────────────────────
function showConfigModal() {
    const modal = document.getElementById('config-modal');
    if (modal) modal.style.display = 'flex';
}

function saveConfig(onSuccess) {
    const url = document.getElementById('input-url').value.trim();
    const key = document.getElementById('input-key').value.trim();
    if (!url || !key) return;
    localStorage.setItem('SUPABASE_URL', url);
    localStorage.setItem('SUPABASE_ANON_KEY', key);
    _supabase = null; // reset singleton
    const modal = document.getElementById('config-modal');
    if (modal) modal.style.display = 'none';
    if (onSuccess) onSuccess();
}

function checkAndBootstrap(onReady) {
    const url = localStorage.getItem('SUPABASE_URL');
    const key = localStorage.getItem('SUPABASE_ANON_KEY');
    const modal = document.getElementById('config-modal');
    const inputUrl = document.getElementById('input-url');
    const inputKey = document.getElementById('input-key');

    if (url && key) {
        if (modal) modal.style.display = 'none';
        if (inputUrl) inputUrl.value = url;
        if (inputKey) inputKey.value = key;
        onReady();
    } else {
        if (modal) modal.style.display = 'flex';
    }
}

// ─── Config modal HTML snippet (injected into pages that need it) ─────────────
const CONFIG_MODAL_HTML = `
<div id="config-modal" style="display:flex;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.85);justify-content:center;align-items:center;z-index:1000;">
  <div style="background:#1e293b;padding:30px;border-radius:12px;border:1px solid #334155;width:420px;">
    <h2 style="margin-top:0;color:#f8fafc;">Database Configuration</h2>
    <p style="color:#94a3b8;font-size:0.9em;margin-bottom:20px;">Required for read-only browser access to Supabase.</p>
    <label style="color:#94a3b8;font-size:0.85em;">Supabase URL</label>
    <input type="text" id="input-url" placeholder="https://xyzcompany.supabase.co"
      style="width:100%;padding:10px;margin:6px 0 16px;box-sizing:border-box;background:#0f172a;border:1px solid #334155;color:white;border-radius:6px;">
    <label style="color:#94a3b8;font-size:0.85em;">Supabase ANON Key</label>
    <input type="password" id="input-key" placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      style="width:100%;padding:10px;margin:6px 0 20px;box-sizing:border-box;background:#0f172a;border:1px solid #334155;color:white;border-radius:6px;">
    <button id="btn-save-config"
      style="width:100%;padding:10px;background:#3b82f6;color:white;border:none;border-radius:6px;cursor:pointer;font-size:16px;">
      Save &amp; Connect
    </button>
  </div>
</div>`;

// ─── Minimum sample floor ─────────────────────────────────────────────────────
const MIN_SAMPLE_FLOOR = 15;

// ─── Insufficient data state renderer ────────────────────────────────────────
function renderInsufficientData(container, sampleCount, floor) {
    const pct = Math.min(100, Math.round((sampleCount / floor) * 100));
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📊</div>
        <h3>Insufficient Data</h3>
        <p>Ranking requires at least <strong>${floor} closed trades</strong>.<br>
           This strategy has <strong>${sampleCount}</strong> so far.</p>
        <div class="progress-bar-wrap">
          <div class="progress-bar" style="width:${pct}%"></div>
        </div>
        <p class="progress-label">${sampleCount} / ${floor} trades recorded</p>
        <p class="empty-note">Strategy is <strong>running in SHADOW mode</strong> — signals are generated but not ranked until the floor is reached.</p>
      </div>`;
}

// ─── No-signals-yet renderer ──────────────────────────────────────────────────
function renderNoSignals(container) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🔍</div>
        <h3>No Signals Yet</h3>
        <p>This strategy has not generated any signals for this symbol yet.<br>
           The system is active and will produce signals when entry conditions align.</p>
        <p class="empty-note">This is expected during early operation. The strategy is healthy.</p>
      </div>`;
}
