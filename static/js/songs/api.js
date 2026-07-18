// static/js/songs/api.js

const SongsAPI = {
    baseUrl: '/api/songs',
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (response.status === 401) {
            window.location.href = '/login';
            throw new Error('Unauthorized');
        }
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || error.message || 'API Error');
        }
        
        return response.json();
    },
    
    // Data & Statistics
    getData(params) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/data?${query}`);
    },
    
    getStatistics() {
        return this.request('/statistics');
    },
    
    // CRUD
    getSong(id) {
        return this.request(`/${id}`);
    },
    
    create(data) {
        return this.request('', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    update(id, data) {
        return this.request(`/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    delete(id) {
        return this.request(`/${id}`, {
            method: 'DELETE'
        });
    },
    
    // Bulk Operations
    bulkUpdateStatus(songIds, status) {
        return this.request('/bulk/status', {
            method: 'PATCH',
            body: JSON.stringify({ song_ids: songIds, status })
        });
    },
    
    bulkUpdateArtist(songIds, artistId) {
        return this.request('/bulk/artist', {
            method: 'PATCH',
            body: JSON.stringify({ song_ids: songIds, artist_id: artistId })
        });
    },
    
    bulkUpdateReleaseDate(songIds, releaseDate) {
        return this.request('/bulk/release-date', {
            method: 'PATCH',
            body: JSON.stringify({ song_ids: songIds, release_date: releaseDate })
        });
    },
    
    bulkDelete(songIds) {
        return this.request('/bulk', {
            method: 'DELETE',
            body: JSON.stringify({ song_ids: songIds })
        });
    },
    
    // Import & Export
    importSongs(songs) {
        return this.request('/import', {
            method: 'POST',
            body: JSON.stringify(songs)
        });
    },
    
    exportPlaylist(day, mode, params = {}) {
        const query = new URLSearchParams({
            mode: mode,
            target: params.target || 160,
            duplicate: params.duplicate || 2,
            channel_limit: params.channel_limit || 2,
            ...params
        }).toString();
        window.location.href = `${this.baseUrl}/export/day/${day}?${query}`;
    },
    
    getExportStatus(mode) {
        return this.request(`/export/status?mode=${mode}`);
    },
    
    exportExists(day, mode) {
        return this.request(`/export/exists?day=${day}&mode=${mode}`);
    },
    
    // Usage
    getUsageBatches(mode = 'normal') {
        return this.request(`/usage?mode=${mode}`);
    },
    
    getUsageDetail(day, mode = 'normal') {
        return this.request(`/usage/day/${day}?mode=${mode}`);
    },
    
    deleteUsageBatch(day, mode = 'normal') {
        return this.request(`/usage/day/${day}?mode=${mode}`, {
            method: 'DELETE'
        });
    },
    
    resetUsage(mode = 'normal') {
        return this.request(`/usage?mode=${mode}`, {
            method: 'DELETE'
        });
    },
    
    // Filters
    getFilters() {
        return this.request('/filters');
    },
    
    getChannels() {
        return this.request('/channels');
    },
    
    getArtists(channelId) {
        const query = channelId ? `?channel_id=${channelId}` : '';
        return this.request(`/artists${query}`);
    }
};