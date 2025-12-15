let currentLang = "tr";
let cachedStrings = null;

export async function loadStrings() {
    if (!cachedStrings) {
        const response = await fetch("../static/assets/strings.json");
        cachedStrings = await response.json();
    }
    return cachedStrings[currentLang];
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