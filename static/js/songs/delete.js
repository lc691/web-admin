// static/js/songs/delete.js

$(document).ready(function() {
    $(document).on('click', '.btn-delete', function() {
        const songId = $(this).data('id');
        const title = $(this).closest('tr').find('td:eq(2)').text().trim() || 'Unknown';
        $('#delete-song-id').val(songId);
        $('#delete-song-title').text(`"${title}"`);
        $('#modal-delete').modal('show');
    });
    
    $('#btn-delete-confirm').on('click', function() {
        const songId = parseInt($('#delete-song-id').val());
        if (!songId) { showToast('Invalid song', 'error'); return; }
        
        const $btn = $(this);
        $btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i> Deleting...');
        
        SongsAPI.delete(songId).then(() => {
            $('#modal-delete').modal('hide');
            if (window.songsTable) window.songsTable.ajax.reload();
            showToast('Lagu berhasil dihapus', 'success');
        }).catch(e => {
            showToast(e.message, 'error');
        }).finally(() => {
            $btn.prop('disabled', false).html('<i class="fas fa-trash me-1"></i> Delete');
        });
    });
});