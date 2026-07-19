/**
 * app.js — Main dashboard controller for AXIS.
 *
 * Revision: Phase 6 + R5 fix.
 * - Unified honesty-state engine (Supabase Realtime + Netlify health + pipeline staleness)
 * - Governance panel poll
 * - Trader session / PRS panel poll
 * - Macro regime / cross-symbol panel poll
 * - Shared Realtime channel (signals feed via shared channel)
 */

let supabase;

function saveConfig() {
    const url = document.getElementById('input-url').value.trim();
    const key = document.getElementById('input-key').value.trim();
    if (url && key) {
        localStorage.setItem('SUPABASE_URL', url);
        localStorage.setItem('SUPABASE_ANON_KEY', key);
        document.getElementById('config-modal').style.display = 'none';
        initApp();
    }
}

function checkConfig() {
    const url = localStorage.getItem('SUPABASE_URL');
    const key = localStorage.getItem('SUPABASE_ANON_KEY');
    if (url && key) {
        document.getElementById('config-modal').style.display = 'none';
        document.getElementById('input-url').value = url;
        document.getElementById('input-key').value = key;
        initApp();
    }
}

function formatTime(isoString) {
    if (!isoString) return '--';
    const d = new Date(isoString);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function timeAgoMinutes(isoString) {
    if (!isoString) return Infinity;
    const diffMs = new Date() - new Date(isoString);
    return Math.floor(diffMs / 60000);
}

function initApp() {
    const url = localStorage.getItem('SUPABASE_URL');
    const key = localStorage.getItem('SUPABASE_ANON_KEY');
    supabase = window.supabase.createClient(url, key);
    window._axisSupabase = supabase; // expose for strategy widget

    // ── Shared Realtime channel (R5 fix: subscribe callback feeds honesty state) ──
    const channel = getSharedChannel(supabase);

    // Also subscribe for live signals feed on the shared channel
    onSharedChannelEvent({
        table: 'signals',
        callback: (_table, row) => renderNewSignal(row),
    });

    // Initial fetch of recent signals to populate feed
    supabase.from('signals')
        .select('*')
        .order('generated_at', { ascending: false })
        .limit(10)
        .then(({ data }) => {
            if (data) {
                data.reverse().forEach(renderNewSignal);
            }
        });

    // ── Polling cadence: every 60 seconds for all panels ──
    pollHealth();
    pollPortfolios();
    pollPaperTrades();
    pollGovernance();
    pollTraderSession();
    pollMacroRegime();
    pollNetlifyHealth();

    setInterval(pollHealth, 60000);
    setInterval(pollPortfolios, 60000);
    setInterval(pollPaperTrades, 60000);
    setInterval(pollGovernance, 60000);
    setInterval(pollTraderSession, 60000);
    setInterval(pollMacroRegime, 60000);
    setInterval(pollNetlifyHealth, 60000);

    // Update honesty banner every 30s (includes IST market-hours check)
    updateHonestyUI();
    setInterval(updateHonestyUI, 30000);

    // Notify strategy widget
    if (typeof window._onSupabaseReady === 'function') window._onSupabaseReady();
}

function renderNewSignal(signal) {
    const container = document.getElementById('signals-container');
    const card = document.createElement('div');
    card.className = 'signal-card';

    // Parse target recommendation safely
    let recStr = 'No recommendation';
    try {
        const conditions = typeof signal.conditions_met === 'string' ? JSON.parse(signal.conditions_met) : (signal.conditions_met || {});
        if (conditions.recommended_strike) {
            recStr = `${conditions.recommended_strike} ${conditions.ce_or_pe || ''} (${conditions.recommended_expiry || ''})`;
        }
    } catch(e) {}

    const ev = signal.ev_rupees ? `₹${signal.ev_rupees}` : '--';

    card.innerHTML = `
        <div class="signal-header">
            <strong style="color: var(--accent-color)">${signal.symbol}</strong>
            <span style="color: var(--text-muted); font-size: 0.9em">${formatTime(signal.generated_at)}</span>
        </div>
        <div style="margin-bottom: 8px;">
            <span>${signal.strategy_name}</span> &bull;
            <span class="verdict-${signal.verifier_verdict}">${signal.verifier_verdict || 'PENDING'}</span>
        </div>
        <div style="font-size: 0.9em; color: var(--text-muted)">
            EV: ${ev} | Target: ${recStr}
        </div>
    `;

    container.insertBefore(card, container.firstChild);

    // Keep only top 50 elements
    while(container.children.length > 50) {
        container.removeChild(container.lastChild);
    }
}


// ═══════════════════════════════════════════════════════════════════════════════
// POLL FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

async function pollHealth() {
    const { data: summaries } = await supabase
        .from('cycle_summaries')
        .select('symbol, cycle_time')
        .order('cycle_time', { ascending: false });

    if (!summaries) return;

    // Get newest for each
    const latest = { NIFTY: null, BANKNIFTY: null };
    for (const row of summaries) {
        if (!latest[row.symbol]) {
            latest[row.symbol] = row;
        }
    }

    let anyStale = false;
    ['NIFTY', 'BANKNIFTY'].forEach(sym => {
        const row = latest[sym];
        const age = timeAgoMinutes(row?.cycle_time);

        const dot = document.getElementById(`dot-${sym.toLowerCase()}`);
        const timeSpan = document.getElementById(`time-${sym.toLowerCase()}`);

        if (age <= 40) {
            if (dot) dot.className = 'dot healthy';
        } else {
            if (dot) dot.className = 'dot dead';
            anyStale = true;
        }

        if (row) {
            if (timeSpan) timeSpan.textContent = `${age}m ago`;
            // Feed into honesty signals
            if (sym === 'NIFTY') _honestySignals.niftyAgeMin = age;
            else _honestySignals.bankniftyAgeMin = age;
        } else {
            if (timeSpan) timeSpan.textContent = 'No data';
        }
    });

    _honestySignals.pipelineStale = anyStale;
    updateHonestyUI();
}

async function pollPortfolios() {
    const { data } = await supabase
        .from('virtual_portfolios')
        .select('*')
        .order('symbol')
        .order('strategy_name');

    if (!data) return;

    const tbody = document.getElementById('portfolios-tbody');
    tbody.innerHTML = '';

    data.forEach(vp => {
        const tr = document.createElement('tr');
        const capital = vp.current_capital || vp.capital || 0;
        const pnl = vp.total_pnl || 0;
        const pnlClass = pnl >= 0 ? 'pnl-positive' : 'pnl-negative';

        const winRate = vp.total_trades > 0
            ? Math.round((vp.winning_trades / vp.total_trades) * 100) + '%'
            : '--';

        tr.innerHTML = `
            <td><strong>${vp.symbol}</strong></td>
            <td>${vp.strategy_name}</td>
            <td>₹${Number(capital).toLocaleString()}</td>
            <td class="${pnlClass}">₹${Number(pnl).toLocaleString()}</td>
            <td>${winRate} (${vp.winning_trades}/${vp.total_trades})</td>
        `;
        tbody.appendChild(tr);
    });
}

async function pollPaperTrades() {
    // Join paper_trades with signals to get symbol and strategy_name
    const { data } = await supabase
        .from('paper_trades')
        .select('*, signals(symbol, strategy_name)')
        .order('entry_time', { ascending: false })
        .limit(20);

    if (!data) return;

    const tbody = document.getElementById('trades-tbody');
    tbody.innerHTML = '';

    data.forEach(trade => {
        const tr = document.createElement('tr');
        const pnl = trade.pnl_rupees || 0;
        const pnlCls = pnl > 0 ? 'pnl-positive' : (pnl < 0 ? 'pnl-negative' : '');

        const sig = trade.signals || {};

        tr.innerHTML = `
            <td style="font-size: 0.85em; color: var(--text-muted)">
                ${formatTime(trade.entry_time)} <br> ${formatTime(trade.exit_time)}
            </td>
            <td>
                <strong>${sig.symbol || '--'}</strong><br>
                <span style="font-size: 0.85em; color: var(--text-muted)">${sig.strategy_name || '--'}</span>
            </td>
            <td>${trade.status}</td>
            <td class="${pnlCls}">₹${Number(pnl).toLocaleString()}</td>
            <td style="font-size: 0.85em; max-width: 150px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${trade.exit_reason || ''}">
                ${trade.exit_reason || '--'}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// ── Governance Activity ────────────────────────────────────────────────────────
async function pollGovernance() {
    const { data } = await supabase
        .from('governance_actions')
        .select('timestamp, gate_name, mode, would_block, did_block, reason')
        .order('timestamp', { ascending: false })
        .limit(15);

    renderGovernancePanel('governance-container', data);
}

// ── Trader Session / PRS ───────────────────────────────────────────────────────
async function pollTraderSession() {
    // Get today's date in IST
    const now = new Date();
    const istStr = now.toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' }); // YYYY-MM-DD

    const { data } = await supabase
        .from('trader_session_state')
        .select('*')
        .eq('trading_date', istStr)
        .order('created_at', { ascending: false });

    renderTraderSessionPanel('prs-container', data);
}

// ── Macro Regime / Cross-Symbol ────────────────────────────────────────────────
async function pollMacroRegime() {
    const { data } = await supabase
        .from('macro_regime_flags')
        .select('signal_timestamp, symbol, direction, session_id')
        .order('signal_timestamp', { ascending: false })
        .limit(10);

    renderMacroRegimePanel('macro-container', data);
}

// ── Honesty State UI Update ────────────────────────────────────────────────────
function updateHonestyUI() {
    renderHonestyBanner('honesty-banner');

    // Also update the realtime badge in the header
    const dot = document.getElementById('dot-realtime');
    const text = document.getElementById('text-realtime');
    const state = computeHonestyState();

    if (dot && text) {
        if (state === HONESTY_STATES.DISCONNECTED) {
            dot.className = 'dot dead';
            text.textContent = 'Disconnected';
            text.style.color = 'var(--red)';
        } else if (state === HONESTY_STATES.STALE) {
            dot.className = 'dot dead';
            text.textContent = 'Stale';
            text.style.color = 'var(--yellow)';
        } else if (state === HONESTY_STATES.MARKET_CLOSED) {
            dot.className = 'dot';
            text.textContent = 'Market Closed';
            text.style.color = 'var(--text-muted)';
        } else {
            dot.className = 'dot healthy';
            text.textContent = 'Connected';
            text.style.color = 'var(--green)';
        }
    }
}

checkConfig();
