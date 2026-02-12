let currentLang = "tr";
let cachedStrings = null;
const STRINGS_PATH = "./static/assets/strings.json";

export async function loadStrings() {
    if (!cachedStrings) {
        try {
            const response = await fetch(STRINGS_PATH);
            cachedStrings = await response.json();
        } catch (err) {
            cachedStrings = { tr: {}, en: {} };
        }
    }
    return cachedStrings[currentLang] || cachedStrings.tr || {};
}

function resolveValue(obj, path) {
    const keys = path.split('.');
    let acc = obj;

    for (const key of keys) {
        if (acc == null) {
            return undefined;
        }
        acc = acc[key];
    }

    return acc;
}

export async function applyStrings() {
    const strings = await loadStrings();

    document.querySelectorAll("[data-key]").forEach(el => {
        const key = el.dataset.key;
        const value = resolveValue(strings, key);

        if (value == null) return;

        el.textContent = value;
        
    });
}

export function getCurrentLang() {
    return currentLang;
}

export function setCurrentLang(lang) {
    currentLang = lang;
}

export async function toggleLanguage() {
    if (getCurrentLang() === "en") {
        setCurrentLang("tr");
    } else {
        setCurrentLang("en");
    }
    document.documentElement.lang = getCurrentLang();
    await applyStrings();
}
