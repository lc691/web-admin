// static/js/songs/filters.js

$(document).ready(function() {
    // ==========================================================
    // LOAD FILTERS FROM API
    // ==========================================================
    
    async function loadFilters() {
        try {
            const response = await fetch('/api/songs/filters', {
                headers: { 'Accept': 'application/json' }
            });
            
            if (!response.ok) {
                console.warn('Filters API returned:', response.status);
                loadFiltersFallback();
                return;
            }
            
            const filters = await response.json();
            populateFilters(filters);
            
        } catch (error) {
            console.warn('Failed to load filters:', error);
            loadFiltersFallback();
        }
    }
    
    // ==========================================================
    // POPULATE FILTERS
    // ==========================================================
    
    function populateFilters(filters) {
        // Status
        const $status = $('#filter-status');
        $status.find('option:not(:first)').remove();
        (filters.statuses || []).forEach(s => {
            $status.append(`<option value="${s.value}">${s.label}</option>`);
        });
        
        // Channels
        const $channel = $('#filter-channel');
        $channel.find('option:not(:first)').remove();
        (filters.channels || []).forEach(c => {
            const count = c.song_count || 0;
            $channel.append(`<option value="${c.id}">${c.name} (${count})</option>`);
        });
        
        // Artists
        const $artist = $('#filter-artist');
        $artist.find('option:not(:first)').remove();
        (filters.artists || []).forEach(a => {
            const count = a.song_count || 0;
            $artist.append(`<option value="${a.id}" data-channel="${a.channel_id}">${a.name} (${count})</option>`);
        });
    }
    
    // ==========================================================
    // FALLBACK - Gunakan data dari HTML jika API gagal
    // ==========================================================
    
    function loadFiltersFallback() {
        // Coba ambil dari window variable
        const filters = window.SONGS_FILTERS || getFiltersFromSelects();
        populateFilters(filters);
    }
    
    function getFiltersFromSelects() {
        // Ambil options yang sudah ada di select
        const statuses = [];
        $('#filter-status option').each(function() {
            const val = $(this).val();
            if (val) {
                statuses.push({ value: val, label: $(this).text() });
            }
        });
        
        const channels = [];
        $('#filter-channel option').each(function() {
            const val = $(this).val();
            if (val) {
                channels.push({ id: parseInt(val), name: $(this).text() });
            }
        });
        
        const artists = [];
        $('#filter-artist option').each(function() {
            const val = $(this).val();
            if (val) {
                artists.push({ 
                    id: parseInt(val), 
                    name: $(this).text(),
                    channel_id: $(this).data('channel') || null
                });
            }
        });
        
        return { statuses, channels, artists };
    }
    
    // ==========================================================
    // FILTER ARTISTS BY CHANNEL
    // ==========================================================
    
    function filterArtistsByChannel(channelId) {
        const $artist = $('#filter-artist');
        const currentVal = $artist.val();
        
        $artist.find('option').each(function() {
            const $opt = $(this);
            const val = $opt.val();
            if (!val) return; // Skip placeholder
            
            const optChannel = $opt.data('channel');
            if (!channelId || optChannel == channelId) {
                $opt.show();
            } else {
                $opt.hide();
            }
        });
        
        // Reset jika pilihan saat ini tidak terlihat
        if (currentVal && $artist.find(`option[value="${currentVal}"]`).is(':hidden')) {
            $artist.val('');
        }
    }
    
    // ==========================================================
    // RELOAD TABLE
    // ==========================================================
    
    function reloadTable() {
        if (window.songsTable) {
            window.songsTable.ajax.reload();
        }
    }
    
    // ==========================================================
    // DEBOUNCE UTILITY
    // ==========================================================
    
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
    
    // ==========================================================
    // EVENT HANDLERS
    // ==========================================================
    
    // Search dengan debounce (400ms)
    $('#filter-keyword').on('keyup', debounce(function() {
        reloadTable();
    }, 400));
    
    // Enter key langsung reload
    $('#filter-keyword').on('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            reloadTable();
        }
    });
    
    // Status filter
    $('#filter-status').on('change', function() {
        reloadTable();
    });
    
    // Channel filter - juga filter artist
    $('#filter-channel').on('change', function() {
        const channelId = $(this).val();
        filterArtistsByChannel(channelId);
        reloadTable();
    });
    
    // Artist filter
    $('#filter-artist').on('change', function() {
        reloadTable();
    });
    
    // ==========================================================
    // RESET FILTERS
    // ==========================================================
    
    $('#btn-reset-filter').on('click', function() {
        // Reset semua input
        $('#filter-keyword').val('');
        $('#filter-status').val('');
        $('#filter-channel').val('');
        $('#filter-artist').val('');
        
        // Tampilkan semua artist
        $('#filter-artist option').show();
        
        // Reload table
        reloadTable();
        
        // Feedback
        showToast('Filters reset', 'success');
    });
    
    // ==========================================================
    // KEYBOARD SHORTCUTS
    // ==========================================================
    
    $(document).on('keydown', function(e) {
        // Ctrl + Shift + R = Reset filters
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'r') {
            e.preventDefault();
            $('#btn-reset-filter').click();
        }
    });
    
    // ==========================================================
    // INIT
    // ==========================================================
    
    // Load filters dari API
    loadFilters();
    
    console.log('Filters module initialized');
});