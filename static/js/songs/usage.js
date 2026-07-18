// static/js/songs/usage.js

$(document).ready(function() {
    let selectedDay = null;
    let selectedMode = 'normal';
    
    $('#btn-usage').on('click', function() {
        $('#modal-usage').modal('show');
        loadBatches();
    });
    
    function loadBatches() {
        const mode = $('#usage-mode').val();
        selectedMode = mode;
        const $select = $('#usage-day');
        $select.html('<option value="">Loading...</option>');
        
        SongsAPI.getUsageBatches(mode).then(data => {
            $select.empty();
            $select.append('<option value="">Select Day</option>');
            if (!data || data.length === 0) {
                $select.append('<option value="">No data</option>');
                return;
            }
            data.sort((a, b) => b.day - a.day);
            data.forEach(item => {
                $select.append(`<option value="${item.day}" data-mode="${item.mode}">Day ${item.day} - ${item.mode} (${item.total_songs || 0})</option>`);
            });
            const first = data[0]?.day;
            if (first) { $select.val(first); loadDetail(first, mode); }
        }).catch(e => {
            $select.html('<option value="">Error</option>');
            showToast('Gagal load usage', 'error');
        });
    }
    
    function loadDetail(day, mode) {
        selectedDay = day;
        const $table = $('#usage-table tbody');
        $table.html('<tr><td colspan="6" class="text-center py-4"><i class="fas fa-spinner fa-spin me-2"></i> Loading...</td></tr>');
        clearSummary();
        
        SongsAPI.getUsageDetail(day, mode).then(data => {
            if (!data) {
                $table.html('<tr><td colspan="6" class="text-center text-muted py-4">No data</td></tr>');
                return;
            }
            updateSummary(data);
            renderSongs(data.songs || []);
        }).catch(e => {
            $table.html(`<tr><td colspan="6" class="text-center text-danger py-4">${e.message}</td></tr>`);
        });
    }
    
    function renderSongs(songs) {
        const $table = $('#usage-table tbody');
        $table.empty();
        if (!songs.length) {
            $table.html('<tr><td colspan="6" class="text-center text-muted py-4">No songs</td></tr>');
            return;
        }
        const badges = { 'Live': 'bg-success', 'Approved': 'bg-warning text-dark', 'Review': 'bg-secondary', 'Take Down': 'bg-danger', 'Topic': 'bg-info' };
        songs.forEach((s, i) => {
            $table.append(`
                <tr>
                    <td class="text-center">${i + 1}</td>
                    <td><span class="badge bg-${getColor(s.channel_name)}">${s.channel_name || '-'}</span></td>
                    <td>${s.artist_name || '-'}</td>
                    <td><strong>${s.title || '-'}</strong></td>
                    <td class="text-center">${s.order || i + 1}</td>
                    <td class="text-center"><span class="badge ${badges[s.status] || 'bg-secondary'}">${s.status || '-'}</span></td>
                </tr>
            `);
        });
    }
    
    function getColor(name) {
        if (!name) return 'secondary';
        const map = { 'amr': 'primary', 'mcl': 'success', 'fkr': 'warning', 'zam': 'info', 'spx': 'danger' };
        const lower = name.toLowerCase();
        for (const [k, v] of Object.entries(map)) {
            if (lower.includes(k)) return v;
        }
        return 'secondary';
    }
    
    function updateSummary(data) {
        const batch = data.batch || {};
        const stats = data.statistics || {};
        const songs = data.songs || [];
        $('#usage-summary-day').text(batch.day || '-');
        $('#usage-summary-mode').text(batch.mode || '-');
        $('#usage-summary-target').text(batch.target || '-');
        $('#usage-summary-duplicate').text(batch.duplicate || '-');
        $('#usage-summary-unique').text(stats.unique_songs || songs.length || '-');
        $('#usage-summary-channels').text(stats.channels || '-');
        $('#usage-summary-artists').text(stats.artists || '-');
        $('#usage-summary-songs').text(songs.length || 0);
        $('#usage-total').text(songs.length + ' Songs');
    }
    
    function clearSummary() {
        ['day', 'mode', 'target', 'duplicate', 'unique', 'channels', 'artists', 'songs'].forEach(f => {
            $(`#usage-summary-${f}`).text('-');
        });
        $('#usage-total').text('0 Songs');
    }
    
    $('#usage-day').on('change', function() {
        const day = $(this).val();
        const mode = $('#usage-mode').val();
        if (day) loadDetail(parseInt(day), mode);
        else clearSummary();
    });
    
    $('#usage-mode').on('change', function() {
        loadBatches();
    });
    
    let searchTimeout;
    $('#usage-search').on('keyup', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const search = $(this).val().toLowerCase();
            let count = 0;
            $('#usage-table tbody tr').each(function() {
                const match = $(this).text().toLowerCase().includes(search);
                $(this).toggle(match);
                if (match) count++;
            });
            $('#usage-total').text(count + ' Songs');
        }, 300);
    });
    
    $('#usage-delete').on('click', function() {
        if (!selectedDay) { showToast('Pilih day dulu', 'warning'); return; }
        if (!confirm(`Delete usage day ${selectedDay}?`)) return;
        const $btn = $(this);
        $btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i> Deleting...');
        SongsAPI.deleteUsageBatch(selectedDay, selectedMode).then(() => {
            showToast(`Day ${selectedDay} deleted`, 'success');
            loadBatches();
            clearSummary();
            $('#usage-table tbody').html('<tr><td colspan="6" class="text-center text-muted py-4">Select a day</td></tr>');
        }).catch(e => showToast(e.message, 'error')).finally(() => {
            $btn.prop('disabled', false).html('<i class="fas fa-trash me-1"></i> Delete');
        });
    });
    
    $('#usage-reset').on('click', function() {
        if (!confirm(`Reset ALL usage for "${selectedMode}"?`)) return;
        if (!confirm('⚠️ Yakin? Tidak bisa dibatalkan!')) return;
        const $btn = $(this);
        $btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i> Resetting...');
        SongsAPI.resetUsage(selectedMode).then(() => {
            showToast('Usage reset', 'success');
            loadBatches();
            clearSummary();
            $('#usage-table tbody').html('<tr><td colspan="6" class="text-center text-muted py-4">Reset complete</td></tr>');
        }).catch(e => showToast(e.message, 'error')).finally(() => {
            $btn.prop('disabled', false).html('<i class="fas fa-refresh me-1"></i> Reset');
        });
    });
    
    $('#usage-export').on('click', function() {
        const rows = [['No', 'Channel', 'Artist', 'Title', 'Order', 'Status']];
        $('#usage-table tbody tr:visible').each(function() {
            const cols = $(this).find('td');
            if (cols.length === 6) {
                rows.push(cols.map((i, el) => $(el).text().trim()).get());
            }
        });
        if (rows.length <= 1) { showToast('No data', 'warning'); return; }
        const csv = rows.map(r => r.join(',')).join('\n');
        const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `usage_${selectedDay || 'all'}_${selectedMode}_${new Date().toISOString().slice(0,10)}.csv`;
        a.click();
        URL.revokeObjectURL(a.href);
        showToast('CSV exported', 'success');
    });
});