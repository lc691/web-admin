// static/js/songs/update.js

$(document).ready(function() {
    $(document).on('click', '.btn-edit', function() {
        const songId = $(this).data('id');
        loadSong(songId);
    });
    
    function loadSong(songId) {
        $('#btn-update-save').prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i> Loading...');
        $('#modal-edit').modal('show');
        
        SongsAPI.getSong(songId).then(song => {
            $('#edit-song-id').val(song.id);
            $('#edit-song-title').val(song.title);
            $('#edit-artist-id').val(song.artist_id);
            
            const channelId = $('#edit-artist-id option:selected').data('channel');
            $('#edit-channel-id').val(channelId);
            filterArtists(channelId);
            $('#edit-artist-id').val(song.artist_id);
            
            $('#edit-song-status').val(song.status);
            $('#edit-release-date').val(song.release_date || '');
        }).catch(e => {
            showToast(e.message, 'error');
            $('#modal-edit').modal('hide');
        }).finally(() => {
            $('#btn-update-save').prop('disabled', false).html('<i class="fas fa-save me-1"></i> Update Song');
        });
    }
    
    function filterArtists(channelId) {
        const $artist = $('#edit-artist-id');
        const val = $artist.val();
        $artist.find('option').each(function() {
            const $opt = $(this);
            if ($opt.val() === '') return;
            $opt.toggle(!channelId || $opt.data('channel') == channelId);
        });
        if (val && $artist.find(`option[value="${val}"]`).is(':hidden')) $artist.val('');
    }
    
    $('#edit-channel-id').on('change', function() {
        filterArtists($(this).val());
        $('#edit-artist-id').val('');
    });
    
    $('#btn-update-save').on('click', function() {
        const data = {
            title: $('#edit-song-title').val().trim(),
            artist_id: parseInt($('#edit-artist-id').val()),
            status: $('#edit-song-status').val(),
            release_date: $('#edit-release-date').val() || null
        };
        
        let valid = true;
        $('#edit-song-form .is-invalid').removeClass('is-invalid');
        if (!data.title) { $('#edit-song-title').addClass('is-invalid'); valid = false; }
        if (!data.artist_id) { $('#edit-artist-id').addClass('is-invalid'); valid = false; }
        if (!valid) { showToast('Isi semua field wajib', 'warning'); return; }
        
        const songId = parseInt($('#edit-song-id').val());
        const $btn = $(this);
        $btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i> Updating...');
        
        SongsAPI.update(songId, data).then(() => {
            $('#modal-edit').modal('hide');
            if (window.songsTable) window.songsTable.ajax.reload();
            showToast('Lagu berhasil diupdate', 'success');
        }).catch(e => {
            showToast(e.message, 'error');
        }).finally(() => {
            $btn.prop('disabled', false).html('<i class="fas fa-save me-1"></i> Update Song');
        });
    });
});