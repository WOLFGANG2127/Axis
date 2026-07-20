/**
 * shared.js — Common utilities for all AXIS dashboard pages.
 * No logic here touches backend Python or makes external API calls
 * beyond Supabase client-side queries and the Netlify health endpoint.
 *
 * Revision: Phase 6 + R5 fix — unified honesty-state engine,
 * governance/PRS/macro rendering helpers, shared Realtime channel.
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
const IST_TZ = 'Asia/Kolkata';

function formatTimeIST(isoString) {
    if (!isoString) return '--';
    return new Date(isoString).toLocaleTimeString('en-IN', {
        timeZone: IST_TZ,
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
}

function formatDateIST(isoString) {
    if (!isoString) return '--';
    return new Date(isoString).toLocaleDateString('en-IN', {
        timeZone: IST_TZ,
        day: '2-digit', month: 'short', year: 'numeric'
    });
}

function formatDateTimeIST(isoString) {
    if (!isoString) return '--';
    return new Date(isoString).toLocaleString('en-IN', {
        timeZone: IST_TZ,
        day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
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
    else if (typeof window.initApp === 'function') window.initApp();
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


// ═══════════════════════════════════════════════════════════════════════════════
// HONESTY-STATE ENGINE (R5 fix + Phase 6)
//
// Three independent signals feed one truth:
//   1. Supabase Realtime .subscribe() status
//   2. Netlify health endpoint fetch (every 60s)
//   3. Pipeline staleness (cycle_summaries age > 40 min)
//
// Priority (highest wins):
//   DISCONNECTED > STALE > MARKET_CLOSED > HEALTHY
// ═══════════════════════════════════════════════════════════════════════════════

const HONESTY_STATES = {
    DISCONNECTED: 'DISCONNECTED',
    STALE:        'STALE',
    MARKET_CLOSED:'MARKET_CLOSED',
    HEALTHY:      'HEALTHY',
};

// Mutable state — written by pollers, read by updateHonestyState
const _honestySignals = {
    realtimeConnected: false,  // Supabase Realtime status === 'SUBSCRIBED'
    netlifyHealthy:    true,   // fetch('/health') returned 200
    pipelineStale:     false,  // newest cycle_summaries > 10 min
    niftyAgeMin:       Infinity,
    bankniftyAgeMin:   Infinity,
};

/**
 * Check if current IST time is within NSE market hours (Mon-Fri 09:15 - 15:30).
 */
function isMarketOpen() {
    const now = new Date();
    const istStr = now.toLocaleString('en-US', { timeZone: IST_TZ });
    const ist = new Date(istStr);
    const day = ist.getDay(); // 0=Sun, 6=Sat
    if (day === 0 || day === 6) return false;
    const hhmm = ist.getHours() * 100 + ist.getMinutes();
    return hhmm >= 915 && hhmm <= 1530;
}

/**
 * Compute the unified honesty state from all three signals.
 */
function computeHonestyState() {
    // Any connection failure → DISCONNECTED (highest priority)
    if (!_honestySignals.realtimeConnected || !_honestySignals.netlifyHealthy) {
        return HONESTY_STATES.DISCONNECTED;
    }
    // Pipeline data is stale → STALE
    if (_honestySignals.pipelineStale) {
        return HONESTY_STATES.STALE;
    }
    // Outside market hours → MARKET_CLOSED
    if (!isMarketOpen()) {
        return HONESTY_STATES.MARKET_CLOSED;
    }
    return HONESTY_STATES.HEALTHY;
}

/**
 * Render the honesty-state banner into the given container element.
 */
function renderHonestyBanner(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;

    const state = computeHonestyState();
    const configs = {
        DISCONNECTED: {
            bg: 'rgba(239,68,68,0.12)',
            border: 'rgba(239,68,68,0.4)',
            icon: '🔴',
            color: '#ef4444',
            title: 'Connection Lost',
            detail: !_honestySignals.realtimeConnected && !_honestySignals.netlifyHealthy
                ? 'Supabase Realtime and Netlify health endpoint both unreachable.'
                : !_honestySignals.realtimeConnected
                    ? 'Supabase Realtime disconnected — live signal feed is interrupted.'
                    : 'Netlify health endpoint unreachable — serverless functions may be down.',
        },
        STALE: {
            bg: 'rgba(245,158,11,0.1)',
            border: 'rgba(245,158,11,0.35)',
            icon: '🟠',
            color: '#f59e0b',
            title: 'Pipeline Stale',
            detail: `Last cycle data is > 10 min old. NIFTY: ${_honestySignals.niftyAgeMin === Infinity ? '--' : _honestySignals.niftyAgeMin + 'm'} · BANKNIFTY: ${_honestySignals.bankniftyAgeMin === Infinity ? '--' : _honestySignals.bankniftyAgeMin + 'm'}. Pipeline may not be running.`,
        },
        MARKET_CLOSED: {
            bg: 'rgba(100,116,139,0.1)',
            border: 'rgba(100,116,139,0.3)',
            icon: '🌙',
            color: '#94a3b8',
            title: 'Market Closed',
            detail: 'NSE market hours: Mon–Fri, 09:15–15:30 IST. Data will refresh at next session open.',
        },
        HEALTHY: {
            bg: 'rgba(16,185,129,0.08)',
            border: 'rgba(16,185,129,0.3)',
            icon: '🟢',
            color: '#10b981',
            title: 'System Healthy',
            detail: 'All connections active. Pipeline running normally.',
        },
    };

    const c = configs[state];
    el.innerHTML = `
        <div style="display:flex;align-items:center;gap:12px;padding:12px 18px;
                    background:${c.bg};border:1px solid ${c.border};border-radius:10px;
                    margin-bottom:20px;font-size:.88rem;line-height:1.5;">
            <span style="font-size:1.1rem;flex-shrink:0">${c.icon}</span>
            <div>
                <strong style="color:${c.color}">${c.title}</strong>
                <span style="color:#94a3b8;margin-left:8px">${c.detail}</span>
            </div>
        </div>`;
}

/**
 * Poll the Netlify health endpoint. Feeds into _honestySignals.
 */
async function pollNetlifyHealth() {
    try {
        const resp = await fetch('/.netlify/functions/health', { signal: AbortSignal.timeout(10000) });
        _honestySignals.netlifyHealthy = resp.ok;
    } catch (_e) {
        _honestySignals.netlifyHealthy = false;
    }
}


// ═══════════════════════════════════════════════════════════════════════════════
// GOVERNANCE PANEL RENDERER
// ═══════════════════════════════════════════════════════════════════════════════

function renderGovernancePanel(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!data || data.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🛡️</div>
                <h3>No Governance Events</h3>
                <p>No governance gate evaluations recorded yet.<br>
                   Events will appear after the first pipeline cycle runs.</p>
            </div>`;
        return;
    }

    container.innerHTML = data.map(a => {
        const status = a.did_block
            ? `<span style="color:var(--red,#ef4444);font-weight:600">BLOCKED</span>`
            : a.would_block
                ? `<span style="color:var(--yellow,#f59e0b);font-weight:600">SHADOW BLOCK</span>`
                : `<span style="color:var(--green,#10b981);font-weight:600">PASS</span>`;
        return `<div style="padding:10px 0;border-bottom:1px solid var(--border,#334155);font-size:.82rem">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <strong>${a.gate_name}</strong>${status}
            </div>
            <div style="color:var(--muted,#64748b);font-size:.78rem;margin-top:2px">
                ${a.mode || 'SHADOW'} · ${formatTimeIST(a.timestamp)}
                ${a.reason ? '<br>' + a.reason.slice(0, 120) : ''}
            </div>
        </div>`;
    }).join('');
}


// ═══════════════════════════════════════════════════════════════════════════════
// TRADER SESSION / PRS PANEL RENDERER
//
// Per Codex Track A handoff: PRS is NOT a simple boolean.
// Block reasons: PRS_NOT_COMPLETED, PRS_MISSING_AFTER_CUTOFF,
// PRS_COMPLETED_AFTER_CUTOFF, PRS_SCORE_BLOCKED, PRS_COMPLETED_AT_MISSING
// ═══════════════════════════════════════════════════════════════════════════════

const PRS_BLOCK_LABELS = {
    PRS_NOT_COMPLETED:        { text: 'Not Completed', color: '#f59e0b', icon: '⏳' },
    PRS_MISSING_AFTER_CUTOFF: { text: 'Missing After 09:10 Cutoff', color: '#ef4444', icon: '🚫' },
    PRS_COMPLETED_AFTER_CUTOFF: { text: 'Completed Late (After 09:10)', color: '#ef4444', icon: '⏰' },
    PRS_SCORE_BLOCKED:        { text: 'Score Too Low', color: '#ef4444', icon: '📉' },
    PRS_COMPLETED_AT_MISSING: { text: 'Completion Timestamp Missing', color: '#f59e0b', icon: '❓' },
};

function renderTraderSessionPanel(containerId, rows) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!rows || rows.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📋</div>
                <h3>No Session State Today</h3>
                <p>Pipeline has not run today, or no PRS quiz completed yet.<br>
                   Session state will appear after the first cycle or PRS submission.</p>
            </div>`;
        return;
    }

    container.innerHTML = rows.map(r => {
        // PRS status
        let prsHtml;
        if (r.prs_completed) {
            if (r.is_trading_blocked && r.prs_block_reason) {
                const lbl = PRS_BLOCK_LABELS[r.prs_block_reason] || { text: r.prs_block_reason, color: '#ef4444', icon: '❌' };
                prsHtml = `<span style="color:${lbl.color};font-weight:600">${lbl.icon} ${lbl.text}</span>`;
            } else {
                prsHtml = `<span style="color:#10b981;font-weight:600">✅ Approved (Score: ${r.prs_score || '--'})</span>`;
            }
        } else if (r.is_trading_blocked && r.prs_block_reason) {
            const lbl = PRS_BLOCK_LABELS[r.prs_block_reason] || { text: r.prs_block_reason, color: '#f59e0b', icon: '⏳' };
            prsHtml = `<span style="color:${lbl.color};font-weight:600">${lbl.icon} ${lbl.text}</span>`;
        } else {
            prsHtml = `<span style="color:#f59e0b;font-weight:600">⏳ Pending</span>`;
        }

        // Circuit breaker
        const cbHtml = r.circuit_breaker_triggered
            ? `<span style="color:#ef4444;font-weight:600">⚡ TRIPPED</span>`
            : `<span style="color:#64748b">Normal</span>`;

        // Cooling off
        const coolHtml = r.cooling_off_until
            ? `<span style="color:#f59e0b">Until ${formatTimeIST(r.cooling_off_until)}</span>`
            : `<span style="color:#64748b">None</span>`;

        const scope = r.symbol === 'ALL' && r.strategy_name === 'ALL'
            ? 'Global'
            : `${r.symbol || 'ALL'} · ${r.strategy_name || 'ALL'}`;

        return `<div style="padding:10px 0;border-bottom:1px solid var(--border,#334155);font-size:.82rem">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                <strong>${scope}</strong>
                ${prsHtml}
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;font-size:.78rem;color:var(--muted-2,#94a3b8)">
                <div>Daily Losses: <strong style="color:var(--text,#f1f5f9)">${r.daily_loss_count || 0}</strong></div>
                <div>Circuit: ${cbHtml}</div>
                <div>Cool-off: ${coolHtml}</div>
            </div>
            ${r.daily_rupee_loss ? `<div style="font-size:.78rem;color:var(--muted,#64748b);margin-top:4px">Daily ₹ loss: <strong class="${pnlClass(-r.daily_rupee_loss)}">${formatINR(r.daily_rupee_loss)}</strong></div>` : ''}
        </div>`;
    }).join('');
}


// ═══════════════════════════════════════════════════════════════════════════════
// MACRO REGIME / CROSS-SYMBOL PANEL RENDERER
// ═══════════════════════════════════════════════════════════════════════════════

function renderMacroRegimePanel(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!data || data.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🌐</div>
                <h3>No Cross-Symbol Flags</h3>
                <p>No macro regime or cross-symbol correlation signals recorded yet.<br>
                   Flags appear when both NIFTY and BANKNIFTY have evaluated in the same window.</p>
            </div>`;
        return;
    }

    container.innerHTML = data.map(r => {
        const dirClass = r.direction === 'BULLISH' ? 'color:#10b981'
            : r.direction === 'BEARISH' ? 'color:#ef4444'
            : 'color:#94a3b8';
        return `<div style="padding:8px 0;border-bottom:1px solid var(--border,#334155);font-size:.82rem;display:flex;justify-content:space-between;align-items:center">
            <div>
                <strong>${r.symbol}</strong>
                <span style="${dirClass};font-weight:600;margin-left:8px">${r.direction}</span>
            </div>
            <span style="color:var(--muted,#64748b);font-size:.75rem">${formatTimeIST(r.signal_timestamp)}</span>
        </div>`;
    }).join('');
}


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


// ═══════════════════════════════════════════════════════════════════════════════
// SHARED REALTIME CHANNEL
//
// ONE channel for all strategy dashboard tabs. Client-side filtering by
// strategy_id prevents N-subscription proliferation.
// ═══════════════════════════════════════════════════════════════════════════════

let _sharedChannel = null;
const _channelListeners = [];

/**
 * Create or return the single shared Realtime channel.
 * Listens for INSERTs on trade_outcomes, governance_actions, and signals.
 * Dispatches to registered listeners with client-side filtering.
 */
function getSharedChannel(sb) {
    if (_sharedChannel) return _sharedChannel;
    if (!sb) return null;

    _sharedChannel = sb
        .channel('axis-shared-feed')
        .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'trade_outcomes' },
            (payload) => _dispatchToListeners('trade_outcomes', payload.new))
        .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'governance_actions' },
            (payload) => _dispatchToListeners('governance_actions', payload.new))
        .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'signals' },
            (payload) => _dispatchToListeners('signals', payload.new))
        .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'macro_regime_flags' },
            (payload) => _dispatchToListeners('macro_regime_flags', payload.new))
        .subscribe((status) => {
            _honestySignals.realtimeConnected = (status === 'SUBSCRIBED');
            
            const honestyBanner = document.getElementById('honesty-banner');
            const dot = document.getElementById('dot-realtime');
            const text = document.getElementById('text-realtime');

            if (status === 'CHANNEL_ERROR' || status === 'CLOSED') {
                if (honestyBanner) {
                    honestyBanner.innerHTML = '<div style="background-color: rgba(245, 158, 11, 0.12); color: #f59e0b; padding: 12px 18px; border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 10px; margin-bottom: 20px; font-weight: bold; display: flex; align-items: center; gap: 12px;"><span style="font-size: 1.1rem;">🟠</span> <span>Reconnecting...</span></div>';
                    honestyBanner.style.display = 'block';
                }
                if (text && dot) {
                    dot.className = 'dot dead';
                    text.textContent = 'Reconnecting...';
                    text.style.color = 'var(--yellow)';
                }
            } else if (status === 'SUBSCRIBED') {
                if (honestyBanner) {
                    honestyBanner.innerHTML = '';
                    honestyBanner.style.display = 'none';
                }
                if (text && dot) {
                    dot.className = 'dot healthy';
                    text.textContent = 'Connected';
                    text.style.color = 'var(--green)';
                }
            }
        });

    return _sharedChannel;
}

function _dispatchToListeners(table, row) {
    _channelListeners.forEach(listener => {
        if (!listener.table || listener.table === table) {
            if (!listener.strategyId || row.strategy_id === listener.strategyId) {
                listener.callback(table, row);
            }
        }
    });
}

/**
 * Register a listener on the shared channel with optional filters.
 * @param {Object} opts - { table, strategyId, callback: (table, row) => void }
 */
function onSharedChannelEvent(opts) {
    _channelListeners.push(opts);
}
