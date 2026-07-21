exports.handler = async function(event, context) {
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_ANON_KEY;
    
    if (!supabaseUrl || !supabaseKey) {
        return { statusCode: 500, body: JSON.stringify({ error: 'Missing environment variables' }) };
    }
    
    const headers = {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Content-Type': 'application/json'
    };
    
    try {
        // Fetch most recent cycle_time for NIFTY
        const niftyReq = fetch(`${supabaseUrl}/rest/v1/cycle_summaries?symbol=eq.NIFTY&select=cycle_time&order=cycle_time.desc&limit=1`, { headers });
        // Fetch most recent cycle_time for BANKNIFTY
        const bankNiftyReq = fetch(`${supabaseUrl}/rest/v1/cycle_summaries?symbol=eq.BANKNIFTY&select=cycle_time&order=cycle_time.desc&limit=1`, { headers });
        
        const [niftyRes, bankNiftyRes] = await Promise.all([niftyReq, bankNiftyReq]);
        
        if (!niftyRes.ok || !bankNiftyRes.ok) {
            return { statusCode: 500, body: JSON.stringify({ error: 'Database query failed' }) };
        }
        
        const niftyData = await niftyRes.json();
        const bankNiftyData = await bankNiftyRes.json();
        
        const niftyRow = niftyData[0];
        const bankNiftyRow = bankNiftyData[0];
        
        if (!niftyRow || !bankNiftyRow) {
            return { 
                statusCode: 200, 
                body: JSON.stringify({ 
                    status: 'stale', 
                    error: 'Missing cycle_summaries for one or both symbols',
                    nifty_age_minutes: Infinity,
                    banknifty_age_minutes: Infinity
                }) 
            };
        }
        
        const now = new Date();
        const niftyTime = new Date(niftyRow.cycle_time);
        const bankNiftyTime = new Date(bankNiftyRow.cycle_time);
        
        const niftyAgeMinutes = (now - niftyTime) / (1000 * 60);
        const bankNiftyAgeMinutes = (now - bankNiftyTime) / (1000 * 60);
        
        if (niftyAgeMinutes > 10 || bankNiftyAgeMinutes > 10) {
            return { 
                statusCode: 200, 
                body: JSON.stringify({
                    status: 'stale',
                    nifty_age_minutes: niftyAgeMinutes,
                    banknifty_age_minutes: bankNiftyAgeMinutes
                }) 
            };
        }
        
        return { 
            statusCode: 200, 
            body: JSON.stringify({
                status: 'healthy',
                nifty_age_minutes: niftyAgeMinutes,
                banknifty_age_minutes: bankNiftyAgeMinutes
            }) 
        };
    } catch (error) {
        return { statusCode: 500, body: JSON.stringify({ error: error.message }) };
    }
};
