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
    const features = await ApiService.getFeatures();
    const formFields = document.getElementById("formFields");
    formFields.innerHTML = "";

    // urun_fiyat hariç tüm alanları form'da göster
    features.forEach((field) => {
      if (field === "urun_fiyat") {
        return; // Fiyat tahmin edilen alan, form'da gösterme
      }

      const fieldGroup = document.createElement("div");
      fieldGroup.className = "form-group";

      const label = document.createElement("label");
      label.htmlFor = field;
      label.textContent = formatFieldName(field);

      const input = document.createElement("input");
      input.type = "text";
      input.id = field;
      input.name = field;
      input.placeholder = `${formatFieldName(field)} girin`;
      input.required = true;

      fieldGroup.appendChild(label);
      fieldGroup.appendChild(input);
      formFields.appendChild(fieldGroup);
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
  document.getElementById("resultSection").style.display = "block";
  document.getElementById("predictedPrice").textContent = `₺ ${price.toLocaleString(
    "tr-TR",
    {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }
  )}`;
  document.getElementById("resultMessage").textContent =
    "Tahmin başarıyla yapıldı!";
}

// Hata göster
function showError(message) {
  document.getElementById("errorSection").style.display = "block";
  document.getElementById("errorMessage").textContent = message;
}
