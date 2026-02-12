const API_BASE_URL = window.__API_BASE_URL__ || 'http://127.0.0.1:5000';
const PREDICT_ENDPOINT = '/predict';
const FEATURES_ENDPOINT = '/get_features';

export async function predict(param) {
    const url = API_BASE_URL + PREDICT_ENDPOINT;
    const data = { param };

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        throw new Error(`predict request failed with status ${response.status}`);
    }

    return response.json();
}

export async function getFeatures() {
    const url = API_BASE_URL + FEATURES_ENDPOINT;
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    if (!response.ok) {
        throw new Error(`get_features request failed with status ${response.status}`);
    }

    const payload = await response.json();
    if (!payload || !Array.isArray(payload.features)) {
        throw new Error('get_features returned invalid payload');
    }

    return payload.features;
}
