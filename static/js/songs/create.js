// static/js/songs/create.js

$(document).ready(function() {
    // ==========================================================
    // LOAD DATA UNTUK FORM CREATE
    // ==========================================================
    
    async function loadCreateFormData() {
        try {
            console.log('Loading create form data...');
            
            // 1. Load Channels
            const channels = await SongsAPI.getChannels();
            console.log('Channels loaded:', channels);
            populateChannels(channels);
            
            // 2. Load Artists
            const artists = await SongsAPI.getArtists();
            console.log('Artists loaded:', artists);
            populateArtists(artists);
            
            // 3. Load Statuses (hardcoded atau dari API)
            const statuses = [
                { value: 'Review', label: 'Review' },
                { value: 'Approved', label: 'Approved' },
                { value: 'Live', label: 'Live' }
            ];
            populateStatuses(statuses);
            
        } catch (error) {
            console.error('Failed to load form data:', error);
            showToast('Gagal memuat data form: ' + error.message, 'error');
            
            // Fallback: coba load dari window
            loadCreateFormDataFallback();
        }
    }
    
    // ==========================================================
    // POPULATE CHANNELS
    // ==========================================================
    
    function populateChannels(channels) {
        const $select = $('#create-channel-id');
        // Hapus semua option kecuali placeholder
        $select.find('option:not(:first)').remove();
        
        if (!channels || channels.length === 0) {
            $select.append('<option value="">No channels available</option>');
            return;
        }
        
        channels.forEach(channel => {
            const option = document.createElement('option');
            option.value = channel.id;
            option.textContent = channel.name;
            $select.append(option);
        });
        
        console.log(`Populated ${channels.length} channels`);
    }
    
    // ==========================================================
    // POPULATE ARTISTS
    // ==========================================================
    
    function populateArtists(artists) {
        const $select = $('#create-artist-id');
        $select.find('option:not(:first)').remove();
        
        if (!artists || artists.length === 0) {
            $select.append('<option value="">No artists available</option>');
            return;
        }
        
        artists.forEach(artist => {
            const option = document.createElement('option');
            option.value = artist.id;
            option.textContent = artist.name;
            option.dataset.channel = artist.channel_id || '';
            $select.append(option);
        });
        
        console.log(`Populated ${artists.length} artists`);
    }
    
    // ==========================================================
    // POPULATE STATUSES
    // ==========================================================
    
    function populateStatuses(statuses) {
        const $select = $('#create-song-status');
        $select.find('option').remove();
        
        if (!statuses || statuses.length === 0) {
            $select.append('<option value="">No statuses available</option>');
            return;
        }
        
        statuses.forEach(status => {
            const option = document.createElement('option');
            option.value = status.value;
            option.textContent = status.label;
            $select.append(option);
        });
        
        console.log(`Populated ${statuses.length} statuses`);
    }
    
    // ==========================================================
    // FALLBACK - Load dari window
    // ==========================================================
    
    function loadCreateFormDataFallback() {
        console.log('Loading fallback data from window...');
        
        // Coba dari window.SONGS_DATA
        const data = window.SONGS_DATA || {};
        
        if (data.channels) {
            populateChannels(data.channels);
        }
        
        if (data.artists) {
            populateArtists(data.artists);
        }
        
        if (data.statuses) {
            populateStatuses(data.statuses);
        } else {
            // Default statuses
            populateStatuses([
                { value: 'Review', label: 'Review' },
                { value: 'Approved', label: 'Approved' },
                { value: 'Live', label: 'Live' }
            ]);
        }
    }
    
    // ==========================================================
    // FILTER ARTISTS BY CHANNEL (Create Form)
    // ==========================================================
    
    function filterArtistsForCreate(channelId) {
        const $artist = $('#create-artist-id');
        const currentVal = $artist.val();
        let visibleCount = 0;
        
        $artist.find('option').each(function() {
            const $opt = $(this);
            const val = $opt.val();
            if (!val) {
                $opt.show();
                return;
            }
            
            const optChannel = $opt.data('channel') || '';
            if (!channelId || String(optChannel) === String(channelId)) {
                $opt.show();
                visibleCount++;
            } else {
                $opt.hide();
            }
        });
        
        // Jika tidak ada artist yang terlihat, tampilkan pesan
        if (visibleCount === 0 && channelId) {
            $artist.find('option:first').show();
            $artist.find('option:first').text('No artists for this channel');
        }
        
        if (currentVal && $artist.find(`option[value="${currentVal}"]`).is(':hidden')) {
            $artist.val('');
        }
        
        console.log(`Filtered artists: ${visibleCount} visible`);
    }
    
    // ==========================================================
    // OPEN CREATE MODAL
    // ==========================================================
    
    $('#btn-create').on('click', function() {
        console.log('Opening create modal...');
        
        // Reset form
        $('#create-song-form')[0].reset();
        $('#create-song-form .is-invalid').removeClass('is-invalid');
        $('#create-artist-id option').show();
        
        // Load data
        loadCreateFormData();
        
        // Show modal
        $('#modal-create').modal('show');
    });
    
    // ==========================================================
    // CHANNEL CHANGE - Filter Artists
    // ==========================================================
    
    $('#create-channel-id').on('change', function() {
        const channelId = $(this).val();
        console.log('Channel changed to:', channelId);
        filterArtistsForCreate(channelId);
        $('#create-artist-id').val('');
    });
    
    // ==========================================================
    // SAVE SONG
    // ==========================================================
    
    $('#btn-create-save').on('click', function() {
        const title = $('#create-song-title').val().trim();
        const artistId = parseInt($('#create-artist-id').val());
        const status = $('#create-song-status').val();
        const releaseDate = $('#create-release-date').val() || null;
        
        console.log('Creating song:', { title, artistId, status, releaseDate });
        
        // Validate
        let valid = true;
        $('#create-song-form .is-invalid').removeClass('is-invalid');
        
        if (!title) {
            $('#create-song-title').addClass('is-invalid');
            valid = false;
        }
        if (!artistId || isNaN(artistId)) {
            $('#create-artist-id').addClass('is-invalid');
            valid = false;
        }
        if (!status) {
            $('#create-song-status').addClass('is-invalid');
            valid = false;
        }
        
        if (!valid) {
            showToast('Isi semua field wajib', 'warning');
            return;
        }
        
        const data = {
            title: title,
            artist_id: artistId,
            status: status,
            release_date: releaseDate
        };
        
        const $btn = $(this);
        $btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i> Saving...');
        
        SongsAPI.create(data)
            .then(() => {
                $('#modal-create').modal('hide');
                if (window.songsTable) {
                    window.songsTable.ajax.reload();
                }
                showToast('Lagu berhasil dibuat', 'success');
            })
            .catch(error => {
                console.error('Create error:', error);
                showToast(error.message || 'Gagal membuat lagu', 'error');
            })
            .finally(() => {
                $btn.prop('disabled', false).html('<i class="fas fa-save me-1"></i> Save Song');
            });
    });
    
    // ==========================================================
    // RESET FORM ON MODAL CLOSE
    // ==========================================================
    
    $('#modal-create').on('hidden.bs.modal', function() {
        console.log('Create modal closed');
        $('#create-song-form')[0].reset();
        $('#create-song-form .is-invalid').removeClass('is-invalid');
        $('#create-artist-id option').show();
    });
    
    // ==========================================================
    // DEBUG: Check if elements exist
    // ==========================================================
    
    console.log('Create form elements:');
    console.log('- #create-channel-id:', $('#create-channel-id').length);
    console.log('- #create-artist-id:', $('#create-artist-id').length);
    console.log('- #create-song-status:', $('#create-song-status').length);
    console.log('- #create-song-title:', $('#create-song-title').length);
    console.log('- #create-release-date:', $('#create-release-date').length);
    
    console.log('Create.js initialized');
});