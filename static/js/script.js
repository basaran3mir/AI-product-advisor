import { applyStrings, getCurrentLang, toggleLanguage } from "./language.js";
import { getFeatures } from "./services/apiService.js";

document.addEventListener("DOMContentLoaded", async () => {
    const fallbackFeatures = [
        "islemci",
        "ram",
        "depolama",
        "ekran_boyutu",
        "batarya_kapasitesi",
        "kamera",
        "malzeme_kalitesi",
        "agirlik",
        "sarj_hizi"
    ];

    const dom = {
        scrollToForm: document.getElementById("scrollToForm"),
        builder: document.getElementById("builder"),
        refreshFeaturesBtn: document.getElementById("refreshFeaturesBtn"),
        featureContainer: document.getElementById("featureContainer"),
        selectedCount: document.getElementById("selectedCount"),
        generateBtn: document.getElementById("generateBtn"),
        results: document.getElementById("results"),
        apiState: document.getElementById("apiState"),
        langBtn: document.getElementById("langBtn"),
        productName: document.getElementById("productName"),
        category: document.getElementById("category"),
        segment: document.getElementById("segment"),
        designTone: document.getElementById("designTone"),
        positioningText: document.getElementById("positioningText"),
        technicalList: document.getElementById("technicalList"),
        designText: document.getElementById("designText"),
        marketingText: document.getElementById("marketingText")
    };

    const groupPriority = [
        "islemci",
        "ram",
        "depolama",
        "ekran",
        "batarya",
        "kamera",
        "malzeme",
        "agirlik",
        "sarj",
        "ag"
    ];

    function normalizeText(value) {
        return value
            .toLocaleLowerCase("tr")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/ı/g, "i");
    }

    function formatFeatureName(feature) {
        return feature
            .split("_")
            .filter(Boolean)
            .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
            .join(" ");
    }

    function detectFeatureGroup(feature) {
        const normalized = normalizeText(feature);

        if (normalized.includes("islemci") || normalized.includes("cpu") || normalized.includes("chip")) return "islemci";
        if (normalized.includes("ram")) return "ram";
        if (normalized.includes("depolama") || normalized.includes("hafiza") || normalized.includes("ssd") || normalized.includes("storage")) return "depolama";
        if (normalized.includes("ekran") || normalized.includes("display")) return "ekran";
        if (normalized.includes("batarya") || normalized.includes("pil") || normalized.includes("battery")) return "batarya";
        if (normalized.includes("kamera") || normalized.includes("camera")) return "kamera";
        if (normalized.includes("malzeme") || normalized.includes("material")) return "malzeme";
        if (normalized.includes("agirlik") || normalized.includes("weight")) return "agirlik";
        if (normalized.includes("sarj") || normalized.includes("charging")) return "sarj";
        if (normalized.includes("ag") || normalized.includes("network")) return "ag";

        const firstToken = feature.split("_").find(Boolean) || feature;
        return normalizeText(firstToken).replace(/\s+/g, "_");
    }

    function groupTitle(groupKey) {
        const labels = {
            tr: {
                islemci: "Islemci",
                ram: "Ram",
                depolama: "Depolama",
                ekran: "Ekran",
                batarya: "Batarya",
                kamera: "Kamera",
                malzeme: "Malzeme",
                agirlik: "Agirlik",
                sarj: "Sarj",
                ag: "Ag"
            },
            en: {
                islemci: "Processor",
                ram: "RAM",
                depolama: "Storage",
                ekran: "Display",
                batarya: "Battery",
                kamera: "Camera",
                malzeme: "Material",
                agirlik: "Weight",
                sarj: "Charging",
                ag: "Network"
            }
        };

        const lang = getCurrentLang();
        return labels[lang]?.[groupKey] || formatFeatureName(groupKey);
    }

    function orderedGroupKeys(groupedFeatures) {
        const keys = Array.from(groupedFeatures.keys());
        const prioritized = groupPriority.filter((key) => groupedFeatures.has(key));
        const rest = keys.filter((key) => !groupPriority.includes(key));
        return [...prioritized, ...rest];
    }

    function updateSelectedCount() {
        const selectedLength = Array.from(
            dom.featureContainer.querySelectorAll("select.feature-select")
        ).filter((select) => select.value).length;

        dom.selectedCount.textContent =
            getCurrentLang() === "en"
                ? `Selected features: ${selectedLength}`
                : `Secilen ozellik: ${selectedLength}`;
    }

    function setApiState(state) {
        const lang = getCurrentLang();
        const labels = {
            tr: {
                idle: "API durumu: Bekleniyor",
                loading: "API durumu: Ozellikler yukleniyor",
                ready: "API durumu: Baglanti basarili",
                error: "API durumu: Baglanti hatasi (yedek liste)"
            },
            en: {
                idle: "API status: Waiting",
                loading: "API status: Loading features",
                ready: "API status: Connected",
                error: "API status: Connection failed (fallback)"
            }
        };

        dom.apiState.dataset.state = state;
        dom.apiState.textContent = labels[lang][state] ?? labels.tr.idle;
    }

    function renderFeatureLoading() {
        dom.featureContainer.innerHTML = "";
        const placeholder = document.createElement("div");
        placeholder.className = "feature-empty";
        placeholder.textContent =
            getCurrentLang() === "en"
                ? "Feature list is loading from /get_features ..."
                : "Ozellik listesi /get_features uzerinden yukleniyor...";
        dom.featureContainer.appendChild(placeholder);
    }

    function renderFeatures(features) {
        dom.featureContainer.innerHTML = "";

        if (!features.length) {
            const empty = document.createElement("div");
            empty.className = "feature-empty";
            empty.textContent =
                getCurrentLang() === "en"
                    ? "No features returned by API."
                    : "API tarafindan ozellik listesi dondurulmedi.";
            dom.featureContainer.appendChild(empty);
            updateSelectedCount();
            return;
        }

        const groupedFeatures = new Map();
        features.forEach((feature) => {
            const groupKey = detectFeatureGroup(feature);
            if (!groupedFeatures.has(groupKey)) {
                groupedFeatures.set(groupKey, []);
            }
            groupedFeatures.get(groupKey).push(feature);
        });

        orderedGroupKeys(groupedFeatures).forEach((groupKey, index) => {
            const dropdown = document.createElement("details");
            dropdown.className = "feature-dropdown";
            if (index === 0) dropdown.open = true;

            const summary = document.createElement("summary");
            summary.textContent = groupTitle(groupKey);

            const body = document.createElement("div");
            body.className = "feature-dropdown-body";

            const select = document.createElement("select");
            select.className = "feature-select";
            select.dataset.featureGroup = groupKey;
            select.ariaLabel = groupTitle(groupKey);

            const emptyOption = document.createElement("option");
            emptyOption.value = "";
            emptyOption.textContent =
                getCurrentLang() === "en"
                    ? "Select an option"
                    : "Bir secenek secin";
            select.appendChild(emptyOption);

            groupedFeatures.get(groupKey).forEach((feature) => {
                const option = document.createElement("option");
                option.value = feature;
                option.textContent = formatFeatureName(feature);
                select.appendChild(option);
            });

            body.appendChild(select);
            dropdown.appendChild(summary);
            dropdown.appendChild(body);
            dom.featureContainer.appendChild(dropdown);
        });

        updateSelectedCount();
    }

    async function loadFeatures() {
        setApiState("loading");
        renderFeatureLoading();

        try {
            const features = await getFeatures();
            renderFeatures(features);
            setApiState("ready");
        } catch (err) {
            console.error("get_features error:", err);
            renderFeatures(fallbackFeatures);
            setApiState("error");
        }
    }

    function profileBySegment(segment) {
        const profiles = {
            giris: {
                position: "erisilebilir fiyat / yuksek kullanilabilirlik",
                performance: "akici gunluk performans",
                design: "islev odakli, sade yuzey dili",
                campaign: "fiyat-performans"
            },
            orta: {
                position: "rekabetci fiyat / dengeli premium algi",
                performance: "uzun omurlu ve guclu kullanim deneyimi",
                design: "net hatlara sahip modern gorunum",
                campaign: "dengeli teknoloji"
            },
            ust: {
                position: "premium fiyat / guclu marka etkisi",
                performance: "ust seviye performans ve yenilik vurgusu",
                design: "rafine malzeme ve iddiali form dili",
                campaign: "amiral gemisi deneyimi"
            }
        };

        return profiles[segment] ?? profiles.orta;
    }

    function technicalSuggestion(feature, segment) {
        const recommendations = {
            giris: {
                ram: "RAM icin minimum 6-8 GB araligi hedeflenmeli.",
                depolama: "Depolama icin en az 128 GB standart sunulmali.",
                batarya: "Batarya kapasitesi gunluk tam kullanim dongusunu karsilamali.",
                ekran: "Ekranda okunabilirlik ve enerji verimliligi dengelenmeli.",
                islemci: "Islemci secimi gundelik uygulamalarda akici deneyim vermeli."
            },
            orta: {
                ram: "RAM kapasitesi 8-12 GB bandinda konumlandirilmali.",
                depolama: "Depolama icin 256 GB ana secenek olarak sunulmali.",
                batarya: "Batarya ve hizli sarj dengesiyle kesintisiz kullanim saglanmali.",
                ekran: "Ekranda yuksek yenileme hizi ve netlik birlikte hedeflenmeli.",
                islemci: "Islemci, coklu gorev performansini surdurulebilir sekilde tasimali."
            },
            ust: {
                ram: "RAM icin en az 12 GB ve ustu yapi planlanmali.",
                depolama: "Depolama katmaninda 512 GB premium standart olmali.",
                batarya: "Batarya sistemi hizli sarj ve uzun dongu dayanimiyla desteklenmeli.",
                ekran: "Ekran teknolojisi renk dogrulugu ve ust seviye akicilik sunmali.",
                islemci: "Islemci performansi AI destekli is yuklerinde fark yaratmali."
            }
        };

        const profile = recommendations[segment] ?? recommendations.orta;
        const lower = feature.toLowerCase();

        if (lower.includes("ram")) return profile.ram;
        if (lower.includes("depolama") || lower.includes("hafiza") || lower.includes("ssd")) return profile.depolama;
        if (lower.includes("batarya") || lower.includes("pil") || lower.includes("sarj")) return profile.batarya;
        if (lower.includes("ekran") || lower.includes("display")) return profile.ekran;
        if (lower.includes("islemci") || lower.includes("cpu") || lower.includes("chip")) return profile.islemci;

        return `${formatFeatureName(feature)} metrigi icin rakip ortalamasinin uzerinde hedef deger belirlenmeli.`;
    }

    function buildPositioning(productName, category, segment, tone) {
        const profile = profileBySegment(segment);
        const toneMap = {
            minimal: "minimal ve temiz",
            sportif: "dinamik ve sportif",
            premium: "premium ve guclu",
            fonksiyonel: "fonksiyonel ve guven veren"
        };

        return `${productName} icin ${category} kategorisinde ${profile.position} ekseninde konumlanma onerilir. Tasarim yaklasimi ${toneMap[tone] ?? "dengeli"} bir dilde kurulmali ve kullaniciya ${profile.performance} mesaji verilmelidir.`;
    }

    function buildDesignAdvice(category, segment, tone) {
        const profile = profileBySegment(segment);
        const toneMap = {
            minimal: "Mat yuzeyler, sade logo alani ve dusuk kontrast gecisler onerilir.",
            sportif: "Keskin hatlar, dinamik vurgu cizgileri ve hareket hissi veren detaylar onerilir.",
            premium: "Metal/cam dokular, kontrollu parlaklik ve guclu tipografik denge onerilir.",
            fonksiyonel: "Ergonomik form, yuksek dayanim hissi ve moduler detaylar onerilir."
        };

        return `${category} urun ailesi icin ${profile.design} yaklasimi benimsenebilir. ${toneMap[tone] ?? ""}`;
    }

    function buildMarketingCopy(productName, category, segment) {
        const profile = profileBySegment(segment);

        return `"${productName}: ${category} kategorisinde ${profile.campaign} yaklasimini yeni nesil kullanici deneyimiyle birlestirir." Kampanya seti icin oneri: 1 ana slogan, 3 kisa sosyal medya varyasyonu, 1 teknik karsilastirma gorsel sablonu.`;
    }

    function selectedFeatures() {
        const selected = Array.from(
            dom.featureContainer.querySelectorAll("select.feature-select")
        )
            .map((select) => select.value)
            .filter(Boolean);

        if (selected.length) return selected;

        return Array.from(
            dom.featureContainer.querySelectorAll("select.feature-select")
        )
            .map((select) => select.options[1]?.value || "")
            .filter(Boolean)
            .slice(0, 4);
    }

    function renderRecommendations(shouldScroll = true) {
        const lang = getCurrentLang();
        const productName = dom.productName.value.trim() || (lang === "en" ? "Untitled Series" : "Isimsiz Seri");
        const category = dom.category.value;
        const segment = dom.segment.value;
        const designTone = dom.designTone.value;
        const features = selectedFeatures().slice(0, 6);

        dom.positioningText.textContent = buildPositioning(productName, category, segment, designTone);
        dom.designText.textContent = buildDesignAdvice(category, segment, designTone);
        dom.marketingText.textContent = buildMarketingCopy(productName, category, segment);

        dom.technicalList.innerHTML = "";
        features.forEach((feature) => {
            const item = document.createElement("li");
            item.textContent = technicalSuggestion(feature, segment);
            dom.technicalList.appendChild(item);
        });

        dom.results.classList.add("active");
        if (shouldScroll) {
            dom.results.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }

    dom.featureContainer.addEventListener("change", updateSelectedCount);
    dom.refreshFeaturesBtn.addEventListener("click", loadFeatures);
    dom.generateBtn.addEventListener("click", renderRecommendations);
    dom.scrollToForm.addEventListener("click", () => {
        dom.builder.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    dom.langBtn.addEventListener("click", async () => {
        await toggleLanguage();
        setApiState(dom.apiState.dataset.state || "idle");
        updateSelectedCount();
        if (dom.results.classList.contains("active")) {
            renderRecommendations(false);
        }
    });

    try {
        await applyStrings();
    } catch (err) {
        console.error("Translation initialization failed:", err);
    }

    setApiState("idle");
    await loadFeatures();
});
