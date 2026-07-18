// static/js/songs/songs.js

$(document).ready(function() {
    console.log('Songs module initialized');
    
    $('#btn-refresh').on('click', function() {
        if (window.songsTable) {
            window.songsTable.ajax.reload();
            showToast('Table refreshed', 'success');
        }
    });
    
    $(document).on('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            if (window.songsTable) {
                window.songsTable.ajax.reload();
                showToast('Table refreshed', 'success');
            }
        }
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            $('#btn-create').click();
        }
        if (e.key === 'Escape') {
            $('.modal.show').modal('hide');
        }
    });
});