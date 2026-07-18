// static/js/songs/release.js

$(document).ready(function() {
    $(document).on('click', '.btn-release', function() {
        const songId = $(this).data('id');
        const date = $(this).data('release') || '';
        $('#release-song-id').val(songId);
        $('#release-date-input').val(date);
        $('#modal-release').modal('show');
    });
    
    $('#release-date-input').on('change', function() {
        const date = $(this).val();
        if (date) {
            $('#release-preview').removeClass('d-none').html(`<i class="fas fa-info-circle me-2"></i> Release date: <strong>${date}</strong>`);
        } else {
            $('#release-preview').removeClass('d-none').html('<i class="fas fa-info-circle me-2"></i> Release date will be <strong>removed</strong>');
        }
    });
    
    $('#btn-release-save').on('click', function() {
        const songId = parseInt($('#release-song-id').val());
        const releaseDate = $('#release-date-input').val() || null;
        if (!songId) { showToast('Invalid song', 'error'); return; }
        
        const $btn = $(this);
        $btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i> Saving...');
        
        SongsAPI.getSong(songId).then(song => {
            return SongsAPI.update(songId, {
                title: song.title,
                artist_id: song.artist_id,
                status: song.status,
                release_date: releaseDate
            });
        }).then(() => {
            $('#modal-release').modal('hide');
            if (window.songsTable) window.songsTable.ajax.reload();
            showToast('Release date updated', 'success');
        }).catch(e => {
            showToast(e.message, 'error');
        }).finally(() => {
            $btn.prop('disabled', false).html('<i class="fas fa-calendar-alt me-1"></i> Save');
        });
    });
});