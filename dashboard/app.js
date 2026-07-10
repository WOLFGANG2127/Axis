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

    // 1. Live signals feed via Supabase Realtime
    supabase
        .channel('signals-feed')
        .on('postgres_changes',
            { event: 'INSERT', schema: 'public', table: 'signals' },
            (payload) => renderNewSignal(payload.new))
        .subscribe();
        
    // Initial fetch of recent signals to populate feed
    supabase.from('signals')
        .select('*')
        .order('generated_at', { ascending: false })
        .limit(10)
        .then(({ data }) => {
            if (data) {
                // Reverse to prepend in chronological order so newest is top
                data.reverse().forEach(renderNewSignal);
            }
        });

    // 2. Per-symbol last-synced indicator
    pollHealth();
    setInterval(pollHealth, 60000);

    // 3. Virtual Portfolios Table
    pollPortfolios();
    setInterval(pollPortfolios, 60000);

    // 4. Paper Trades Table
    pollPaperTrades();
    setInterval(pollPaperTrades, 60000);
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
    
    ['NIFTY', 'BANKNIFTY'].forEach(sym => {
        const row = latest[sym];
        const age = timeAgoMinutes(row?.cycle_time);
        
        const dot = document.getElementById(`dot-${sym.toLowerCase()}`);
        const timeSpan = document.getElementById(`time-${sym.toLowerCase()}`);
        
        if (age <= 40) {
            dot.className = 'dot healthy';
        } else {
            dot.className = 'dot dead';
        }
        
        if (row) {
            timeSpan.textContent = `${age}m ago`;
        } else {
            timeSpan.textContent = 'No data';
        }
    });
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
        const pnlClass = pnl > 0 ? 'pnl-positive' : (pnl < 0 ? 'pnl-negative' : '');
        
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
            <td class="${pnlClass}">₹${Number(pnl).toLocaleString()}</td>
            <td style="font-size: 0.85em; max-width: 150px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${trade.exit_reason || ''}">
                ${trade.exit_reason || '--'}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

checkConfig();
