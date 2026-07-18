// static/js/songs/bulk.js

$(document).ready(function() {
    let selectedIds = [];
    
    $('#check-all').on('change', function() {
        const checked = this.checked;
        $('.row-check').prop('checked', checked);
        updateSelection();
    });
    
    $(document).on('change', '.row-check', function() {
        updateSelection();
        const total = $('.row-check').length;
        const checked = $('.row-check:checked').length;
        $('#check-all').prop('checked', total > 0 && checked === total);
    });
    
    function updateSelection() {
        selectedIds = getSelectedIds();
        $('#bulk-selected-count').text(selectedIds.length + ' songs selected');
        updateBulkButtons();
    }
    
    function showBulkModal(action) {
        if (selectedIds.length === 0) {
            showToast('Pilih minimal 1 lagu', 'warning');
            return;
        }
        $('#bulk-selected-count').text(selectedIds.length + ' songs selected');
        $('#bulk-action').val(action);
        $('#bulk-status-container, #bulk-artist-container, #bulk-release-container, #bulk-delete-warning').addClass('d-none');
        
        if (action === 'status') $('#bulk-status-container').removeClass('d-none');
        else if (action === 'artist') $('#bulk-artist-container').removeClass('d-none');
        else if (action === 'release_date') $('#bulk-release-container').removeClass('d-none');
        else if (action === 'delete') $('#bulk-delete-warning').removeClass('d-none');
        
        $('#modal-bulk').modal('show');
        $('#modal-bulk').data('song-ids', selectedIds);
    }
    
    $('#btn-bulk-status').on('click', function() { showBulkModal('status'); });
    $('#btn-bulk-artist').on('click', function() { showBulkModal('artist'); });
    $('#btn-bulk-release').on('click', function() { showBulkModal('release_date'); });
    $('#btn-bulk-delete').on('click', function() { showBulkModal('delete'); });
    
    $('#bulk-action').on('change', function() {
        const action = $(this).val();
        $('#bulk-status-container, #bulk-artist-container, #bulk-release-container, #bulk-delete-warning').addClass('d-none');
        if (action === 'status') $('#bulk-status-container').removeClass('d-none');
        else if (action === 'artist') $('#bulk-artist-container').removeClass('d-none');
        else if (action === 'release_date') $('#bulk-release-container').removeClass('d-none');
        else if (action === 'delete') $('#bulk-delete-warning').removeClass('d-none');
    });
    
    $('#btn-bulk-submit').on('click', function() {
        const ids = $('#modal-bulk').data('song-ids') || [];
        const action = $('#bulk-action').val();
        
        if (!action) { showToast('Pilih aksi', 'warning'); return; }
        if (ids.length === 0) { showToast('Tidak ada lagu dipilih', 'warning'); return; }
        
        const $btn = $(this);
        $btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i> Processing...');
        
        let promise;
        let msg;
        
        switch(action) {
            case 'status':
                const status = $('#bulk-status').val();
                if (!status) { showToast('Pilih status', 'warning'); $btn.prop('disabled', false).html('Apply'); return; }
                if (!confirm(`Update ${ids.length} lagu ke "${status}"?`)) { $btn.prop('disabled', false).html('Apply'); return; }
                promise = SongsAPI.bulkUpdateStatus(ids, status);
                msg = `${ids.length} lagu diupdate ke ${status}`;
                break;
            case 'artist':
                const artistId = $('#bulk-artist').val();
                if (!artistId) { showToast('Pilih artist', 'warning'); $btn.prop('disabled', false).html('Apply'); return; }
                if (!confirm(`Pindahkan ${ids.length} lagu ke artist terpilih?`)) { $btn.prop('disabled', false).html('Apply'); return; }
                promise = SongsAPI.bulkUpdateArtist(ids, parseInt(artistId));
                msg = `${ids.length} lagu dipindahkan`;
                break;
            case 'release_date':
                const date = $('#bulk-release-date').val();
                if (date && !confirm(`Update release date untuk ${ids.length} lagu?`)) { $btn.prop('disabled', false).html('Apply'); return; }
                if (!date && !confirm(`Hapus release date untuk ${ids.length} lagu?`)) { $btn.prop('disabled', false).html('Apply'); return; }
                promise = SongsAPI.bulkUpdateReleaseDate(ids, date || null);
                msg = `Release date diupdate untuk ${ids.length} lagu`;
                break;
            case 'delete':
                if (!confirm(`Hapus ${ids.length} lagu secara permanen?`)) { $btn.prop('disabled', false).html('Apply'); return; }
                if (!confirm(`⚠️ Yakin? Ini tidak bisa dibatalkan!`)) { $btn.prop('disabled', false).html('Apply'); return; }
                promise = SongsAPI.bulkDelete(ids);
                msg = `${ids.length} lagu dihapus`;
                break;
            default:
                showToast('Aksi tidak valid', 'error');
                $btn.prop('disabled', false).html('Apply');
                return;
        }
        
        promise.then(() => {
            $('#modal-bulk').modal('hide');
            if (window.songsTable) window.songsTable.ajax.reload();
            $('#check-all').prop('checked', false);
            updateSelection();
            showToast(msg, 'success');
        }).catch(e => {
            showToast(e.message, 'error');
        }).finally(() => {
            $btn.prop('disabled', false).html('Apply');
        });
    });
});