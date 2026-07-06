/**
 * Read-only Qdrant gateway for Chesssy theory search.
 *
 * Required Cloudflare Worker environment variables:
 * - QDRANT_URL: https://your-cluster.qdrant.io:6333
 * - QDRANT_API_KEY: read-only Qdrant API key
 * - QDRANT_COLLECTION: chess_theory
 *
 * The browser calls this Worker instead of calling Qdrant directly. The Worker
 * handles CORS and keeps the Qdrant key out of client-side code.
 */

const CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
};

function json(data, status = 200) {
    return new Response(JSON.stringify(data), {
        status,
        headers: {
            ...CORS_HEADERS,
            "Content-Type": "application/json",
        },
    });
}

function isAllowedPath(pathname, collection) {
    return (
        pathname === `/collections/${collection}/points/query` ||
        pathname === `/collections/${collection}/points/scroll`
    );
}

export default {
    async fetch(request, env) {
        if (request.method === "OPTIONS") {
            return new Response(null, { status: 204, headers: CORS_HEADERS });
        }

        if (request.method !== "POST") {
            return json({ error: "Only POST requests are supported." }, 405);
        }

        const collection = env.QDRANT_COLLECTION || "chess_theory";
        const url = new URL(request.url);

        if (!isAllowedPath(url.pathname, collection)) {
            return json({ error: "Route not found." }, 404);
        }

        if (!env.QDRANT_URL || !env.QDRANT_API_KEY) {
            return json({ error: "Qdrant gateway is not configured." }, 500);
        }

        const qdrantUrl = new URL(url.pathname, env.QDRANT_URL);
        const body = await request.text();

        const qdrantResponse = await fetch(qdrantUrl.toString(), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "api-key": env.QDRANT_API_KEY,
            },
            body,
        });

        return new Response(qdrantResponse.body, {
            status: qdrantResponse.status,
            headers: {
                ...CORS_HEADERS,
                "Content-Type": qdrantResponse.headers.get("Content-Type") || "application/json",
            },
        });
    },
};
