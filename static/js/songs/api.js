class SongAPI {
    constructor(baseURL = "/songs") {
        this.baseURL = baseURL;
    }

    buildURL(path = "", params = {}) {
        const url = new URL(
            this.baseURL + path,
            window.location.origin
        );

        Object.entries(params).forEach(([key, value]) => {
            if (
                value !== null &&
                value !== undefined &&
                value !== ""
            ) {
                if (Array.isArray(value)) {
                    value.forEach(v =>
                        url.searchParams.append(key, v)
                    );
                } else {
                    url.searchParams.append(key, value);
                }
            }
        });

        return url.toString();
    }

    async request(
        method,
        path = "",
        {
            params = {},
            body = null,
            headers = {},
        } = {},
    ) {
        const options = {
            method,
            credentials: "same-origin",
            headers: {
                ...headers,
            },
        };

        if (body instanceof FormData) {
            options.body = body;
        } else if (body !== null) {
            options.headers["Content-Type"] = "application/json";
            options.body = JSON.stringify(body);
        }

        const response = await fetch(
            this.buildURL(path, params),
            options,
        );

        const contentType =
            response.headers.get("content-type") || "";

        let data;

        if (contentType.includes("application/json")) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        if (!response.ok) {
            throw new Error(
                data?.detail ||
                data?.message ||
                response.statusText
            );
        }

        return data;
    }

    /* =======================================================
       LIST
    ======================================================= */

    list(params) {
        return this.request("GET", "", {
            params,
        });
    }

    /* =======================================================
       DETAIL
    ======================================================= */

    detail(id) {
        return this.request(
            "GET",
            `/${id}`,
        );
    }

    /* =======================================================
       CREATE
    ======================================================= */

    create(data) {
        return this.request(
            "POST",
            "",
            {
                body: data,
            },
        );
    }

    /* =======================================================
       UPDATE
    ======================================================= */

    update(id, data) {
        return this.request(
            "PUT",
            `/${id}`,
            {
                body: data,
            },
        );
    }

    /* =======================================================
       DELETE
    ======================================================= */

    delete(id) {
        return this.request(
            "DELETE",
            `/${id}`,
        );
    }

    /* =======================================================
       STATISTICS
    ======================================================= */

    getStatistics() {
        return this.request(
            "GET",
            "/statistics",
        );
    }

    /* =======================================================
       IMPORT
    ======================================================= */

    import(data) {
        return this.request(
            "POST",
            "/import",
            {
                body: data,
            },
        );
    }

    /* =======================================================
       BULK
    ======================================================= */

    bulkStatus(song_ids, status) {
        return this.request(
            "PATCH",
            "/bulk/status",
            {
                params: {
                    status,
                },
                body: song_ids,
            },
        );
    }

    bulkArtist(song_ids, artist_id) {
        return this.request(
            "PATCH",
            "/bulk/artist",
            {
                params: {
                    artist_id,
                },
                body: song_ids,
            },
        );
    }

    bulkRelease(song_ids, release_date) {
        return this.request(
            "PATCH",
            "/bulk/release-date",
            {
                params: {
                    release_date,
                },
                body: song_ids,
            },
        );
    }

    bulkDelete(song_ids) {
        return this.request(
            "DELETE",
            "/bulk",
            {
                body: song_ids,
            },
        );
    }

    /* =======================================================
       EXPORT
    ======================================================= */

    exportStatus(mode = "normal") {
        return this.request(
            "GET",
            "/export/status",
            {
                params: {
                    mode,
                },
            },
        );
    }

    exportPlaylist(
        day,
        {
            mode = "normal",
            target = 160,
            duplicate = 2,
            channel_limit = 2,
            excluded_channels = [],
        } = {},
    ) {
        return this.request(
            "GET",
            `/export/day/${day}`,
            {
                params: {
                    mode,
                    target,
                    duplicate,
                    channel_limit,
                    excluded_channels,
                },
            },
        );
    }

    /* =======================================================
       USAGE
    ======================================================= */

    usageBatches(mode = "normal") {
        return this.request(
            "GET",
            "/usage",
            {
                params: {
                    mode,
                },
            },
        );
    }

    usage(day, mode = "normal") {
        return this.request(
            "GET",
            `/usage/day/${day}`,
            {
                params: {
                    mode,
                },
            },
        );
    }

    deleteUsage(day, mode = "normal") {
        return this.request(
            "DELETE",
            `/usage/day/${day}`,
            {
                params: {
                    mode,
                },
            },
        );
    }

    resetUsage(mode = "normal") {
        return this.request(
            "DELETE",
            "/usage",
            {
                params: {
                    mode,
                },
            },
        );
    }
}

window.SongAPI = new SongAPI();