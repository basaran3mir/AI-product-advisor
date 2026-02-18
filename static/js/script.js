// Sayfa yüklendikten sonra form alanlarını hazırla
document.addEventListener("DOMContentLoaded", async () => {
  await loadFormFields();

  // Form submit olayını dinle
  document.getElementById("predictForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    await handlePrediction();
  });
});

// Form alanlarını API'den al ve oluştur
async function loadFormFields() {
  try {
    const categories = await ApiService.getCategories();
    const formFields = document.getElementById("formFields");
    formFields.innerHTML = "";

    Object.entries(categories).forEach(([cat, fields]) => {
      if (fields.length === 0) return;
      const section = document.createElement("div");
      section.className = "form-category";

      const title = document.createElement("h3");
      title.className = "form-category-title";
      title.textContent = cat;
      section.appendChild(title);

      fields.forEach((fieldObj) => {
        const fieldGroup = document.createElement("div");
        fieldGroup.className = "form-group";

        const label = document.createElement("label");
        label.htmlFor = fieldObj.name;
        // Birimi label'a ekle
        label.textContent = formatFieldName(fieldObj.label) + (fieldObj.unit ? ` (${fieldObj.unit})` : "");

        // Dropdown (select) oluştur
        const select = document.createElement("select");
        select.id = fieldObj.name;
        select.name = fieldObj.name;
        select.required = true;

        // Varsayılan boş seçenek
        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = `${formatFieldName(fieldObj.label)}${fieldObj.unit ? ` (${fieldObj.unit})` : ""} seçin`;
        defaultOption.disabled = true;
        defaultOption.selected = true;
        select.appendChild(defaultOption);

        // Değerleri ekle (birimi option'a ekleme, sadece değeri göster)
        (fieldObj.values || []).forEach((val) => {
          const option = document.createElement("option");
          option.value = val;
          option.textContent = val;
          select.appendChild(option);
        });

        fieldGroup.appendChild(label);
        fieldGroup.appendChild(select);
        // Birimi ayrıca sağda göstermek isterseniz:
        // if (fieldObj.unit) {
        //   const unitSpan = document.createElement("span");
        //   unitSpan.className = "unit-label";
        //   unitSpan.textContent = fieldObj.unit;
        //   fieldGroup.appendChild(unitSpan);
        // }
        section.appendChild(fieldGroup);
      });
      formFields.appendChild(section);
    });
  } catch (error) {
    showError("Form alanları yüklenemedi: " + error.message);
  }
}

// Sınıf adını okunaklı hale getir
function formatFieldName(fieldName) {
  return fieldName
    .replace(/_/g, " ")
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

// Tahmin yap
async function handlePrediction() {
  try {
    // Hata ve sonuç bölümünü gizle
    document.getElementById("errorSection").style.display = "none";
    document.getElementById("resultSection").style.display = "none";

    // Form verilerini topla
    const formData = new FormData(document.getElementById("predictForm"));
    const inputData = {};

    for (let [key, value] of formData.entries()) {
      inputData[key] = value;
    }

    // Tahmin al
    const predictedPrice = await ApiService.predictPrice(inputData);

    // Sonucu göster
    showResult(predictedPrice);
  } catch (error) {
    showError("Tahmin yapılırken hata: " + error.message);
  }
}

// Sonucu göster
function showResult(price) {
  const formattedPrice = `₺ ${price.toLocaleString("tr-TR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;

  document.getElementById("resultSection").style.display = "block";
  document.getElementById("predictedPrice").textContent = formattedPrice;

  const corporatePriceEl = document.getElementById("corporatePrice");
  if (corporatePriceEl) {
    corporatePriceEl.textContent = formattedPrice;
  }

  const confidenceRangeEl = document.getElementById("confidenceRange");
  const confidenceFillEl = document.getElementById("confidenceFill");
  const confidenceScoreEl = document.getElementById("confidenceScore");
  if (confidenceRangeEl) {
    const rangePercent = 8;
    const confidenceScore = Math.max(0, Math.min(100, 100 - rangePercent));

    confidenceRangeEl.textContent = `±${rangePercent}%`;

    if (confidenceFillEl) {
      confidenceFillEl.style.width = `${confidenceScore}%`;
    }
    if (confidenceScoreEl) {
      confidenceScoreEl.textContent = `Skor: ${confidenceScore}/100`;
    }
  }

  document.getElementById("resultMessage").textContent =
    "Tahmin başarıyla yapıldı!";
}

// Hata göster
function showError(message) {
  document.getElementById("errorSection").style.display = "block";
  document.getElementById("errorMessage").textContent = message;
}
