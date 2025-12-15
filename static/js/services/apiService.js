const public_api_url = "http://127.0.0.1:5000"
const predict_url_end = "/predict";

export async function predict(param) {
    const url = public_api_url + predict_url_end;
    const data = {
        'param': param
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const responseData = await response.json();

        return responseData

    } catch (error) {
        console.error('Error:', error);
        return {
            'return_code': 'error'
        };
    }
}