import { applyStrings } from './language.js';
import { predict } from './services/apiService.js';

document.addEventListener('DOMContentLoaded', async () => {

    // declaritons
    const btn = document.getElementById('generateBtn');
    const results = document.getElementById('results');

    // apply string
    try {
        await applyStrings();
    }
    catch (err) {
        console.error('Initialization failed:', err);
    }

    // init
    let initDone = false;

    function init() {
        if (initDone) return;
        initDone = true;

        setOnClickers()
    }

    // functions
    function setOnClickers() {
        btn.addEventListener('click', () => {
            results.classList.add('active');
            results.scrollIntoView({ behavior: 'smooth' });
        });
    }

    init()

});