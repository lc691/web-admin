// static/js/songs/export.js

$(document).ready(function() {
    let selectedDay = 1;
    
    $('#btn-export').on('click', function() {
        $('#modal-export').modal('show');
        loadStatus();
        renderDays();
    });
    
    function loadStatus() {
        const mode = $('#export-mode').val();
        SongsAPI.getExportStatus(mode).then(data => {
            data.forEach(item => {
                const $day = $(`.export-day[data-day="${item.day}"]`);
                if ($day.length) {
                    const status = item.completed ? '✅ Done' : 
                                  item.exported > 0 ? `${item.exported}/${item.target_unique}` : '📝 Ready';
                    $day.find('.export-status').text(status);
                    if (item.completed) $day.addClass('border-success');
                }
            });
        }).catch(e => console.error(e));
    }
    
    function renderDays() {
        const $container = $('#export-days');
        $container.empty();
        for (let i = 1; i <= 30; i++) {
            const $col = $(`
                <div class="col-md-2 col-4">
                    <div class="card export-day border-0 shadow-sm" data-day="${i}">
                        <div class="card-body text-center p-2">
                            <div class="h5 fw-bold mb-0 text-primary">Day ${i}</div>
                            <div class="small text-muted export-status">Loading...</div>
                        </div>
                    </div>
                </div>
            `);
            $col.find('.export-day').on('click', function() { selectDay(i); });
            $container.append($col);
        }
        selectDay(1);
    }
    
    function selectDay(day) {
        selectedDay = day;
        $('.export-day').removeClass('border-primary');
        $(`.export-day[data-day="${day}"]`).addClass('border-primary');
        $('#export-day').val(day);
        $('#selected-day-title').text(`Day ${day}`);
        loadDayDetail(day);
    }
    
    function loadDayDetail(day) {
        const mode = $('#export-mode').val();
        $('#selected-status').html('<span class="badge bg-warning"><i class="fas fa-spinner fa-spin me-1"></i> Loading...</span>');
        
        SongsAPI.getExportStatus(mode).then(data => {
            const item = data.find(d => d.day === day);
            if (item) {
                const progress = item.completed ? 100 : Math.min((item.exported / item.target_unique) * 100, 100);
                $('#selected-progress').css('width', progress + '%');
                if (item.completed) {
                    $('#selected-status').html('<span class="badge bg-success">✅ Completed</span>');
                } else if (item.exported > 0) {
                    $('#selected-status').html(`<span class="badge bg-info">${item.exported}/${item.target_unique}</span>`);
                } else {
                    $('#selected-status').html('<span class="badge bg-primary">▶️ Ready</span>');
                }
                $('#estimated-unique').text(item.target_unique || 0);
                $('#estimated-playlist').text(item.target || 0);
                $('#estimated-duplicate').text(`×${item.duplicate || 1}`);
                $('#selected-target').text(item.target || 0);
                $('#selected-exported').text(item.exported || 0);
                $('#selected-remaining').text(Math.max((item.target_unique || 0) - (item.exported || 0), 0));
            } else {
                const target = parseInt($('#export-target').val()) || 160;
                const dup = parseInt($('#export-duplicate').val()) || 2;
                $('#selected-status').html('<span class="badge bg-primary">▶️ Ready</span>');
                $('#selected-progress').css('width', '0%');
                $('#estimated-unique').text(Math.ceil(target / dup));
                $('#estimated-playlist').text(target);
                $('#estimated-duplicate').text(`×${dup}`);
                $('#selected-target').text(target);
                $('#selected-exported').text(0);
                $('#selected-remaining').text(Math.ceil(target / dup));
            }
        }).catch(() => {
            $('#selected-status').html('<span class="badge bg-danger">❌ Error</span>');
        });
    }
    
    $('#export-mode').on('change', function() { loadStatus(); if (selectedDay) loadDayDetail(selectedDay); });
    $('#export-target, #export-duplicate').on('change input', function() {
        const target = parseInt($('#export-target').val()) || 160;
        const dup = parseInt($('#export-duplicate').val()) || 2;
        $('#estimated-unique').text(Math.ceil(target / dup));
        $('#estimated-playlist').text(target);
        $('#estimated-duplicate').text(`×${dup}`);
    });
    
    $('#btn-export-run').on('click', function() {
        const day = parseInt($('#export-day').val()) || 1;
        const mode = $('#export-mode').val();
        const target = parseInt($('#export-target').val()) || 160;
        const duplicate = parseInt($('#export-duplicate').val()) || 2;
        const channelLimit = parseInt($('#export-channel-limit').val()) || 2;
        
        const $btn = $(this);
        $btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i> Exporting...');
        
        SongsAPI.exportPlaylist(day, mode, { target, duplicate, channel_limit: channelLimit });
        
        setTimeout(() => {
            $btn.prop('disabled', false).html('<i class="fas fa-file-export me-1"></i> Export Playlist');
            showToast(`Exporting day ${day}...`, 'success');
            loadStatus();
            if (selectedDay) loadDayDetail(selectedDay);
        }, 1500);
    });
});