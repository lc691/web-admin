// static/js/songs/table.js

$(document).ready(function() {
    if ($.fn.DataTable.isDataTable('#songs-table')) {
        $('#songs-table').DataTable().destroy();
    }
    
    const table = $('#songs-table').DataTable({
        processing: true,
        serverSide: true,
        pageLength: 25,
        order: [[1, 'desc']],
        orderCellsTop: true,
        scrollX: true,
        
        ajax: {
            url: '/api/songs/data',
            type: 'GET',
            data: function(d) {
                // =============================================
                // HANYA KIRIM PARAMETER YANG VALID
                // =============================================
                const params = {
                    draw: d.draw || 1,
                    start: d.start || 0,
                    length: d.length || 25
                };
                
                // Keyword - hanya jika ada nilai
                const keyword = d.search?.value || '';
                if (keyword) {
                    params.keyword = keyword;
                }
                
                // Status - hanya jika ada nilai
                const status = $('#filter-status').val();
                if (status) {
                    params.status = status;
                }
                
                // Channel ID - parseInt hanya jika ada nilai
                const channelId = $('#filter-channel').val();
                if (channelId) {
                    params.channel_id = parseInt(channelId);
                }
                
                // Artist ID - parseInt hanya jika ada nilai
                const artistId = $('#filter-artist').val();
                if (artistId) {
                    params.artist_id = parseInt(artistId);
                }
                
                // Order - hanya jika ada
                if (d.order && d.order.length > 0) {
                    params.order_column = d.order[0].column || 1;
                    params.order_dir = d.order[0].dir || 'desc';
                }
                
                console.log('DataTables Request:', params);
                return params;
            },
            error: function(xhr, status, error) {
                console.error('DataTables Error:', status, error);
                console.error('Response:', xhr.responseText);
                
                let msg = 'Gagal memuat data. ';
                if (xhr.status === 422) {
                    msg += 'Parameter tidak valid. ';
                    try {
                        const res = JSON.parse(xhr.responseText);
                        if (res.detail) {
                            const errors = res.detail.map(e => 
                                `${e.loc.join('.')}: ${e.msg}`
                            ).join('; ');
                            msg += errors;
                        }
                    } catch(e) {}
                } else {
                    try {
                        const res = JSON.parse(xhr.responseText);
                        msg += res.detail || res.message || '';
                    } catch(e) {}
                }
                
                $('#table-information').html(
                    `<span class="text-danger"><i class="fas fa-exclamation-triangle me-1"></i>${msg}</span>`
                );
                
                if (xhr.status === 401) {
                    window.location.href = '/login';
                }
            }
        },
        
        columns: [
            {
                data: null,
                orderable: false,
                render: function(data) {
                    return `<input type="checkbox" class="row-check form-check-input" value="${data.id}">`;
                }
            },
            { data: 'id', orderable: true, className: 'fw-bold text-muted' },
            { data: 'title', orderable: true, render: function(d) { return `<span class="fw-medium">${d}</span>`; } },
            { data: 'artist_name', orderable: true },
            { data: 'channel_name', orderable: true },
            {
                data: 'status',
                orderable: true,
                className: 'text-center',
                render: function(data) {
                    const badges = {
                        'Live': 'badge bg-success text-white',
                        'Approved': 'badge bg-warning text-white',
                        'Review': 'badge bg-secondary text-white',
                        'Take Down': 'badge bg-danger text-white',
                        'Topic': 'badge bg-info text-white'
                    };
                    return `<span class="${badges[data] || 'badge bg-secondary text-white'}">${data}</span>`;
                }
            },
            { data: 'release_date', orderable: true, render: function(d) { return d || '-'; } },
            {
                data: null,
                orderable: false,
                className: 'text-end',
                render: function(data) {
                    return `
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary btn-edit" data-id="${data.id}" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-danger btn-delete" data-id="${data.id}" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    `;
                }
            }
        ],
        
        language: {
            processing: '<i class="fas fa-spinner fa-spin me-1"></i> Loading...',
            lengthMenu: 'Show _MENU_ entries',
            zeroRecords: 'No songs found',
            info: 'Showing _START_ to _END_ of _TOTAL_ songs',
            infoEmpty: 'No songs available',
            infoFiltered: '(filtered from _MAX_ total songs)',
            paginate: {
                first: '<i class="fas fa-angle-double-left"></i>',
                previous: '<i class="fas fa-angle-left"></i>',
                next: '<i class="fas fa-angle-right"></i>',
                last: '<i class="fas fa-angle-double-right"></i>'
            }
        },
        
        drawCallback: function() {
            updateSelectedCount();
            updateBulkButtons();
            $('#table-information').html('<i class="fas fa-check-circle text-success me-1"></i> Loaded');
        }
    });
    
    window.songsTable = table;
});

function getSelectedIds() {
    return $('.row-check:checked').map(function() { return $(this).val(); }).get();
}

function updateSelectedCount() {
    $('#selected-counter').text(getSelectedIds().length + ' selected');
}

function updateBulkButtons() {
    const disabled = getSelectedIds().length === 0;
    $('#btn-bulk-status, #btn-bulk-artist, #btn-bulk-release, #btn-bulk-delete').prop('disabled', disabled);
}