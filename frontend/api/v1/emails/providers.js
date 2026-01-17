/**
 * Vercel Serverless Function - Proxy para listar providers
 */

const { GoogleAuth } = require('google-auth-library');

const CLOUD_RUN_URL = process.env.CLOUD_RUN_URL || 'https://email-classifier-api-881402891442.southamerica-east1.run.app';

let tokenCache = { token: null, expiry: 0 };

async function getIdToken() {
    const now = Date.now();

    if (tokenCache.token && tokenCache.expiry > now + 300000) {
        return tokenCache.token;
    }

    const credentials = JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_KEY || '{}');

    if (!credentials.client_email) {
        throw new Error('GOOGLE_SERVICE_ACCOUNT_KEY não configurada');
    }

    const auth = new GoogleAuth({ credentials });
    const client = await auth.getIdTokenClient(CLOUD_RUN_URL);
    const headers = await client.getRequestHeaders();

    const token = headers.Authorization?.replace('Bearer ', '');

    tokenCache = { token, expiry: now + 3600000 };
    return token;
}

module.exports = async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Método não permitido' });
    }

    try {
        const idToken = await getIdToken();
        const targetUrl = `${CLOUD_RUN_URL}/api/v1/emails/providers`;

        console.log(`[Providers Proxy] GET ${targetUrl}`);

        const response = await fetch(targetUrl, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${idToken}`,
            },
        });

        const responseData = await response.text();

        res.setHeader('Content-Type', 'application/json');
        res.status(response.status);

        try {
            return res.json(JSON.parse(responseData));
        } catch {
            return res.send(responseData);
        }

    } catch (error) {
        console.error('[Providers Proxy Error]', error);
        return res.status(500).json({
            error: 'Erro ao buscar providers',
            message: error.message,
            timestamp: new Date().toISOString()
        });
    }
};
