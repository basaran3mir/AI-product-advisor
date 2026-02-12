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
        const tokens = featureTokens(feature);

        if (normalized.includes("islemci") || normalized.includes("cpu") || normalized.includes("chip")) return "islemci";
        if (normalized.includes("kamera") || normalized.includes("camera")) return "kamera";
        if (tokens.includes("ram")) return "ram";
        if (normalized.includes("depolama") || normalized.includes("hafiza") || normalized.includes("ssd") || normalized.includes("storage")) return "depolama";
        if (normalized.includes("ekran") || normalized.includes("display")) return "ekran";
        if (normalized.includes("batarya") || normalized.includes("pil") || normalized.includes("battery")) return "batarya";
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

    function processorSubgroupKey(feature) {
        const normalized = normalizeText(feature);

        if (
            normalized.includes("grafik") ||
            normalized.includes("gpu") ||
            normalized.includes("graphics")
        ) return "gpu";

        if (
            (normalized.includes("yardimci") && normalized.includes("islemci")) ||
            normalized.includes("coprocessor") ||
            normalized.includes("koprocessor")
        ) return "coprocessor";

        if (
            normalized.includes("yonga") ||
            normalized.includes("chipset")
        ) return "chipset";

        return "cpu";
    }

    function processorSubgroupTitle(subgroupKey) {
        const labels = {
            tr: {
                cpu: "CPU (Ana islemci)",
                gpu: "GPU (Grafik)",
                coprocessor: "Yardimci islemciler / koprocessorler",
                chipset: "Yonga seti (Chipset)"
            },
            en: {
                cpu: "CPU (Main processor)",
                gpu: "GPU (Graphics)",
                coprocessor: "Auxiliary processors / coprocessors",
                chipset: "Chipset"
            }
        };

        const lang = getCurrentLang();
        return labels[lang]?.[subgroupKey] || formatFeatureName(subgroupKey);
    }

    function processorFeatureLabel(feature) {
        const normalized = normalizeText(feature);

        if (normalized.includes("ana") && normalized.includes("islemci") && normalized.includes("cpu")) {
            return "Temel Donanim Ana Islemci Cpu";
        }
        if (normalized.includes("cpu") && normalized.includes("cekirdek")) {
            return "Temel Donanim Cpu Cekirdegi";
        }
        if (normalized.includes("cpu") && normalized.includes("frekans")) {
            return "Temel Donanim Cpu Frekansi";
        }
        if (normalized.includes("islemci") && normalized.includes("mimari")) {
            return "Temel Donanim Islemci Mimarisi";
        }
        if (normalized.includes("cpu") && normalized.includes("uretim")) {
            return "Temel Donanim Cpu Uretim Teknolojisi";
        }
        if (normalized.includes("grafik") && normalized.includes("islemci") && normalized.includes("gpu")) {
            return "Temel Donanim Grafik Islemcisi Gpu";
        }
        if (normalized.includes("1") && normalized.includes("yardimci") && normalized.includes("islemci")) {
            return "Temel Donanim 1. Yardimci Islemci";
        }
        if (normalized.includes("2") && normalized.includes("yardimci") && normalized.includes("islemci")) {
            return "Temel Donanim 2. Yardimci Islemci";
        }
        if (normalized.includes("diger") && normalized.includes("chipset")) {
            return "Temel Donanim Diger Chipset Secenekleri";
        }
        if (normalized.includes("yonga") && normalized.includes("chipset")) {
            return "Temel Donanim Yonga Seti Chipset";
        }

        return formatFeatureName(feature);
    }

    function processorFeatureRank(feature) {
        const normalized = normalizeText(feature);

        if (normalized.includes("ana") && normalized.includes("islemci") && normalized.includes("cpu")) return 10;
        if (normalized.includes("cpu") && normalized.includes("cekirdek")) return 20;
        if (normalized.includes("cpu") && normalized.includes("frekans")) return 30;
        if (normalized.includes("islemci") && normalized.includes("mimari")) return 40;
        if (normalized.includes("cpu") && normalized.includes("uretim")) return 50;
        if (normalized.includes("grafik") && normalized.includes("islemci") && normalized.includes("gpu")) return 60;
        if (normalized.includes("1") && normalized.includes("yardimci") && normalized.includes("islemci")) return 70;
        if (normalized.includes("2") && normalized.includes("yardimci") && normalized.includes("islemci")) return 80;
        if (normalized.includes("yonga") && normalized.includes("chipset")) return 90;
        if (normalized.includes("diger") && normalized.includes("chipset")) return 100;

        return 999;
    }

    function hasAny(text, needles) {
        return needles.some((needle) => text.includes(needle));
    }

    function featureTokens(feature) {
        const normalized = normalizeText(feature)
            .replace(/[^a-z0-9_ ]+/g, " ")
            .replace(/\s+/g, " ")
            .trim();

        return normalized.split(/[_ ]+/).filter(Boolean);
    }

    function compactTokensForGroup(tokens, groupKey) {
        const prefixesByGroup = {
            islemci: [["temel", "donanim"]],
            ram: [["temel", "donanim"]],
            depolama: [["temel", "donanim"]],
            ekran: [["ekran"]],
            batarya: [["batarya"]],
            kamera: [["kamera"]],
            malzeme: [["tasarim"]],
            agirlik: [["tasarim"]],
            sarj: [["batarya"]],
            ag: [["ag", "baglantilari"], ["kablosuz", "baglantilar"], ["diger", "baglantilar"]],
            tasarim: [["tasarim"]],
            ozellikler: [["ozellikler"]],
            isletim: [["isletim", "sistemi"]],
            urun: [["urun"]],
            coklu: [["coklu", "ortam"]],
            temel: [["temel", "bilgiler"]]
        };

        let compacted = [...tokens];
        const prefixes = prefixesByGroup[groupKey] || [];

        for (const prefix of prefixes) {
            const isMatch = prefix.every((part, idx) => compacted[idx] === part);
            if (isMatch) {
                compacted = compacted.slice(prefix.length);
                break;
            }
        }

        while (compacted.length > 1 && compacted[0] === compacted[1]) {
            compacted = compacted.slice(1);
        }

        return compacted.length ? compacted : tokens;
    }

    function formatToken(token) {
        const fixedTokens = {
            cpu: "CPU",
            gpu: "GPU",
            ram: "RAM",
            nfc: "NFC",
            usb: "USB",
            ois: "OIS",
            ios: "iOS",
            wifi: "Wi-Fi",
            wi: "Wi",
            fi: "Fi",
            sim: "SIM",
            sar: "SAR",
            ai: "AI",
            hd: "HD",
            qhd: "QHD",
            uhd: "UHD",
            led: "LED",
            fps: "FPS",
            ip: "IP",
            ab: "AB",
            "2g": "2G",
            "3g": "3G",
            "4g": "4G",
            "5g": "5G"
        };

        if (fixedTokens[token]) {
            return fixedTokens[token];
        }

        if (/^v\d+$/i.test(token)) {
            return token.toUpperCase();
        }

        if (/^\d+[a-z]*$/i.test(token)) {
            return token.toLowerCase();
        }

        return token.charAt(0).toUpperCase() + token.slice(1);
    }

    function genericFeatureLabel(feature, groupKey) {
        const tokens = compactTokensForGroup(featureTokens(feature), groupKey);
        if (!tokens.length) return formatFeatureName(feature);

        return tokens.map((token) => formatToken(token)).join(" ");
    }

    function detectFeatureSubgroup(groupKey, feature) {
        if (groupKey === "islemci") return processorSubgroupKey(feature);

        const normalized = normalizeText(feature).replace(/\s+/g, "_");

        switch (groupKey) {
            case "ram":
                if (hasAny(normalized, ["tip"])) return "tip";
                if (hasAny(normalized, ["kanal"])) return "kanal";
                if (hasAny(normalized, ["secenek"])) return "secenek";
                return "kapasite";
            case "depolama":
                if (hasAny(normalized, ["hafiza_karti", "kart_destegi", "karti"])) return "kart";
                if (hasAny(normalized, ["bicim"])) return "bicim";
                if (hasAny(normalized, ["secenek"])) return "secenek";
                return "kapasite";
            case "ekran":
                if (hasAny(normalized, ["teknoloji", "oled", "amoled", "lcd", "pls"])) return "panel";
                if (hasAny(normalized, ["cozunurluk", "piksel"])) return "cozunurluk";
                if (hasAny(normalized, ["yenileme"])) return "yenileme";
                if (hasAny(normalized, ["boyut", "alan", "oran"])) return "boyut";
                if (hasAny(normalized, ["dayaniklilik"])) return "dayaniklilik";
                return "diger";
            case "batarya":
                if (hasAny(normalized, ["hizli_sarj", "kablosuz_sarj", "sarj"])) return "sarj";
                if (hasAny(normalized, ["kapasite", "mah"])) return "kapasite";
                if (hasAny(normalized, ["video", "muzik", "oyun", "internet", "konusma", "bekleme"])) return "sure";
                if (hasAny(normalized, ["dongu", "teknoloji", "degisir"])) return "teknoloji";
                return "diger";
            case "kamera":
                if (hasAny(normalized, ["on_kamera"])) return "on_kamera";
                if (hasAny(normalized, ["video", "fps"])) return "video";
                if (hasAny(normalized, ["diyafram", "ois", "odak", "yakinlastirma", "flas"])) return "optik";
                if (hasAny(normalized, ["arka_kamera", "cozunurlugu", "kamera"])) return "arka_kamera";
                return "diger";
            case "malzeme":
                if (hasAny(normalized, ["govde", "malzeme", "kapak", "cerceve", "metal", "plastik", "cam"])) return "govde";
                if (hasAny(normalized, ["renk"])) return "renk";
                return "diger";
            case "agirlik":
                if (hasAny(normalized, ["agirlik", "kalinlik", "boy", "en"])) return "olcu";
                if (hasAny(normalized, ["secenek"])) return "secenek";
                return "diger";
            case "sarj":
                if (hasAny(normalized, ["kablosuz"])) return "kablosuz";
                if (hasAny(normalized, ["hizli"])) return "hizli";
                if (hasAny(normalized, ["guc", "sure", "dongu"])) return "performans";
                return "genel";
            case "ag":
                if (hasAny(normalized, ["wifi", "bluetooth", "nfc", "navigasyon", "kizilotesi"])) return "kablosuz";
                if (hasAny(normalized, ["2g", "3g", "4g", "5g", "frekans", "indirme", "yukleme", "baglanti"])) return "hucresel";
                if (hasAny(normalized, ["sim", "hat"])) return "sim";
                if (hasAny(normalized, ["usb"])) return "baglanti";
                return "diger";
            case "tasarim":
                if (hasAny(normalized, ["boy", "en", "kalinlik", "agirlik"])) return "olcu";
                if (hasAny(normalized, ["malzeme", "kapak", "cerceve"])) return "malzeme";
                if (hasAny(normalized, ["renk"])) return "renk";
                return "diger";
            case "ozellikler":
                if (hasAny(normalized, ["dayaniklilik", "suya", "toza", "ip"])) return "dayaniklilik";
                if (hasAny(normalized, ["sensor", "parmak", "led"])) return "sensor";
                if (hasAny(normalized, ["sar", "degeri"])) return "guvenlik";
                if (hasAny(normalized, ["servis", "uygulama", "kutu", "aksesuar"])) return "servis";
                return "diger";
            case "isletim":
                if (hasAny(normalized, ["isletim_sistemi", "arayuz", "versiyon"])) return "platform";
                if (hasAny(normalized, ["yukseltilebilir", "planlanan"])) return "guncelleme";
                return "diger";
            case "urun":
                if (hasAny(normalized, ["ad", "url", "seri", "alt_seri"])) return "kimlik";
                if (hasAny(normalized, ["fiyat", "puan"])) return "deger";
                return "diger";
            case "coklu":
                if (hasAny(normalized, ["ses", "hoparlor"])) return "ses";
                if (hasAny(normalized, ["radyo"])) return "radyo";
                return "diger";
            case "temel":
                if (hasAny(normalized, ["cikis", "duyurulma", "tarih", "yil"])) return "zaman";
                if (hasAny(normalized, ["seri", "ad", "kullanim_amaci"])) return "kimlik";
                return "diger";
            default:
                return "genel";
        }
    }

    function subgroupOrderFor(groupKey) {
        const orders = {
            islemci: ["cpu", "gpu", "coprocessor", "chipset"],
            ram: ["kapasite", "tip", "kanal", "secenek", "diger"],
            depolama: ["kapasite", "kart", "bicim", "secenek", "diger"],
            ekran: ["boyut", "cozunurluk", "yenileme", "panel", "dayaniklilik", "diger"],
            batarya: ["kapasite", "sarj", "sure", "teknoloji", "diger"],
            kamera: ["arka_kamera", "on_kamera", "video", "optik", "diger"],
            malzeme: ["govde", "renk", "diger"],
            agirlik: ["olcu", "secenek", "diger"],
            sarj: ["hizli", "kablosuz", "performans", "genel", "diger"],
            ag: ["hucresel", "kablosuz", "sim", "baglanti", "diger"],
            tasarim: ["olcu", "malzeme", "renk", "diger"],
            ozellikler: ["dayaniklilik", "sensor", "guvenlik", "servis", "diger"],
            isletim: ["platform", "guncelleme", "diger"],
            urun: ["kimlik", "deger", "diger"],
            coklu: ["ses", "radyo", "diger"],
            temel: ["zaman", "kimlik", "diger"]
        };

        return orders[groupKey] || ["genel", "diger"];
    }

    function subgroupTitle(groupKey, subgroupKey) {
        if (groupKey === "islemci") return processorSubgroupTitle(subgroupKey);

        const titles = {
            tr: {
                ram: {
                    kapasite: "RAM Kapasitesi",
                    tip: "RAM Tipi",
                    kanal: "RAM Kanal Yapisi",
                    secenek: "RAM Secenekleri",
                    diger: "Diger RAM"
                },
                depolama: {
                    kapasite: "Dahili Depolama",
                    kart: "Hafiza Karti",
                    bicim: "Depolama Bicimi",
                    secenek: "Depolama Secenekleri",
                    diger: "Diger Depolama"
                },
                ekran: {
                    boyut: "Boyut ve Alan",
                    cozunurluk: "Cozunurluk",
                    yenileme: "Yenileme Hizlari",
                    panel: "Panel Teknolojisi",
                    dayaniklilik: "Dayaniklilik",
                    diger: "Diger Ekran Alanlari"
                },
                batarya: {
                    kapasite: "Batarya Kapasitesi",
                    sarj: "Sarj Ozellikleri",
                    sure: "Kullanim Sureleri",
                    teknoloji: "Batarya Teknolojisi",
                    diger: "Diger Batarya Alanlari"
                },
                kamera: {
                    arka_kamera: "Arka Kamera",
                    on_kamera: "On Kamera",
                    video: "Video Ozellikleri",
                    optik: "Optik ve Lens",
                    diger: "Diger Kamera Alanlari"
                },
                malzeme: {
                    govde: "Govde ve Malzeme",
                    renk: "Renk Secenekleri",
                    diger: "Diger Malzeme Alanlari"
                },
                agirlik: {
                    olcu: "Olcu ve Agirlik",
                    secenek: "Agirlik Secenekleri",
                    diger: "Diger Boyut Alanlari"
                },
                sarj: {
                    hizli: "Hizli Sarj",
                    kablosuz: "Kablosuz Sarj",
                    performans: "Sarj Performansi",
                    genel: "Genel Sarj Alanlari",
                    diger: "Diger Sarj Alanlari"
                },
                ag: {
                    hucresel: "Hucresel Baglantilar",
                    kablosuz: "Kablosuz Baglantilar",
                    sim: "SIM ve Hat",
                    baglanti: "Baglanti Portlari",
                    diger: "Diger Ag Alanlari"
                },
                tasarim: {
                    olcu: "Olcu ve Form",
                    malzeme: "Malzeme ve Govde",
                    renk: "Renkler",
                    diger: "Diger Tasarim Alanlari"
                },
                ozellikler: {
                    dayaniklilik: "Dayaniklilik",
                    sensor: "Sensor ve Biyometri",
                    guvenlik: "Guvenlik Degerleri",
                    servis: "Servis ve Icerik",
                    diger: "Diger Ozellikler"
                },
                isletim: {
                    platform: "Platform ve Arayuz",
                    guncelleme: "Guncelleme Durumu",
                    diger: "Diger Isletim Alanlari"
                },
                urun: {
                    kimlik: "Urun Kimligi",
                    deger: "Fiyat ve Puan",
                    diger: "Diger Urun Alanlari"
                },
                coklu: {
                    ses: "Ses Ozellikleri",
                    radyo: "Radyo",
                    diger: "Diger Multimedya"
                },
                temel: {
                    zaman: "Cikis ve Tarih",
                    kimlik: "Urun Bilgileri",
                    diger: "Diger Temel Bilgiler"
                },
                genel: {
                    genel: "Genel",
                    diger: "Diger"
                }
            },
            en: {
                ram: {
                    kapasite: "RAM Capacity",
                    tip: "RAM Type",
                    kanal: "RAM Channels",
                    secenek: "RAM Options",
                    diger: "Other RAM"
                },
                depolama: {
                    kapasite: "Internal Storage",
                    kart: "Memory Card",
                    bicim: "Storage Format",
                    secenek: "Storage Options",
                    diger: "Other Storage"
                },
                ekran: {
                    boyut: "Size and Area",
                    cozunurluk: "Resolution",
                    yenileme: "Refresh Rates",
                    panel: "Panel Technology",
                    dayaniklilik: "Durability",
                    diger: "Other Display Fields"
                },
                batarya: {
                    kapasite: "Battery Capacity",
                    sarj: "Charging",
                    sure: "Usage Duration",
                    teknoloji: "Battery Technology",
                    diger: "Other Battery Fields"
                },
                kamera: {
                    arka_kamera: "Rear Camera",
                    on_kamera: "Front Camera",
                    video: "Video Features",
                    optik: "Optics and Lens",
                    diger: "Other Camera Fields"
                },
                malzeme: {
                    govde: "Body and Material",
                    renk: "Color Options",
                    diger: "Other Material Fields"
                },
                agirlik: {
                    olcu: "Dimensions and Weight",
                    secenek: "Weight Options",
                    diger: "Other Dimension Fields"
                },
                sarj: {
                    hizli: "Fast Charging",
                    kablosuz: "Wireless Charging",
                    performans: "Charging Performance",
                    genel: "General Charging",
                    diger: "Other Charging Fields"
                },
                ag: {
                    hucresel: "Cellular Connectivity",
                    kablosuz: "Wireless Connectivity",
                    sim: "SIM and Line",
                    baglanti: "Ports",
                    diger: "Other Network Fields"
                },
                tasarim: {
                    olcu: "Dimensions and Form",
                    malzeme: "Material and Body",
                    renk: "Colors",
                    diger: "Other Design Fields"
                },
                ozellikler: {
                    dayaniklilik: "Durability",
                    sensor: "Sensors and Biometrics",
                    guvenlik: "Safety Values",
                    servis: "Service and Content",
                    diger: "Other Features"
                },
                isletim: {
                    platform: "Platform and UI",
                    guncelleme: "Upgrade Status",
                    diger: "Other OS Fields"
                },
                urun: {
                    kimlik: "Product Identity",
                    deger: "Price and Rating",
                    diger: "Other Product Fields"
                },
                coklu: {
                    ses: "Audio Features",
                    radyo: "Radio",
                    diger: "Other Media"
                },
                temel: {
                    zaman: "Release and Dates",
                    kimlik: "Product Info",
                    diger: "Other Basics"
                },
                genel: {
                    genel: "General",
                    diger: "Other"
                }
            }
        };

        const lang = getCurrentLang();
        return (
            titles[lang]?.[groupKey]?.[subgroupKey]
            || titles.tr[groupKey]?.[subgroupKey]
            || titles[lang]?.genel?.[subgroupKey]
            || titles.tr.genel[subgroupKey]
            || formatFeatureName(subgroupKey)
        );
    }

    function featureOptionLabel(groupKey, feature) {
        if (groupKey === "islemci") return processorFeatureLabel(feature);
        return genericFeatureLabel(feature, groupKey);
    }

    function sortFeaturesWithinSubgroup(groupKey, featureA, featureB) {
        if (groupKey === "islemci") {
            const rankDiff = processorFeatureRank(featureA) - processorFeatureRank(featureB);
            if (rankDiff !== 0) return rankDiff;
        }

        const labelA = featureOptionLabel(groupKey, featureA);
        const labelB = featureOptionLabel(groupKey, featureB);
        return labelA.localeCompare(labelB, "tr");
    }

    function appendFeatureOptions(container, groupKey, features) {
        const subgroupMap = new Map();
        const preferredOrder = subgroupOrderFor(groupKey);

        features.forEach((feature) => {
            const subgroupKey = detectFeatureSubgroup(groupKey, feature);
            if (!subgroupMap.has(subgroupKey)) {
                subgroupMap.set(subgroupKey, []);
            }
            subgroupMap.get(subgroupKey).push(feature);
        });

        const subgroupKeys = Array.from(subgroupMap.keys());
        const orderedSubgroups = [
            ...preferredOrder.filter((key) => subgroupMap.has(key)),
            ...subgroupKeys
                .filter((key) => !preferredOrder.includes(key))
                .sort((a, b) => a.localeCompare(b, "tr"))
        ];

        orderedSubgroups.forEach((subgroupKey, index) => {
            const subgroupFeatures = subgroupMap.get(subgroupKey) || [];
            if (!subgroupFeatures.length) return;

            subgroupFeatures.sort((a, b) => sortFeaturesWithinSubgroup(groupKey, a, b));

            const subgroupDropdown = document.createElement("details");
            subgroupDropdown.className = "feature-sub-dropdown";
            if (index === 0) subgroupDropdown.open = true;

            const subgroupSummary = document.createElement("summary");
            subgroupSummary.textContent = subgroupTitle(groupKey, subgroupKey);

            const subgroupBody = document.createElement("div");
            subgroupBody.className = "feature-sub-dropdown-body";

            const select = document.createElement("select");
            select.className = "feature-select";
            select.dataset.featureGroup = groupKey;
            select.dataset.featureSubgroup = subgroupKey;
            select.ariaLabel = subgroupTitle(groupKey, subgroupKey);

            subgroupFeatures.forEach((feature) => {
                const option = document.createElement("option");
                option.value = feature;
                option.textContent = featureOptionLabel(groupKey, feature);
                select.appendChild(option);
            });
            select.selectedIndex = -1;

            subgroupBody.appendChild(select);
            subgroupDropdown.appendChild(subgroupSummary);
            subgroupDropdown.appendChild(subgroupBody);
            container.appendChild(subgroupDropdown);
        });
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
                : "Özellik listesi /get_features uzerinden yukleniyor...";
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
            appendFeatureOptions(body, groupKey, groupedFeatures.get(groupKey));
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
            .map((select) => select.options[0]?.value || "")
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
