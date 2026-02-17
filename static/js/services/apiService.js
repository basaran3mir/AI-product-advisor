const API_BASE_URL = "http://127.0.0.1:5000";

class ApiService {
  // Kategorili form alanlarını al
  static async getCategories() {
    try {
      const response = await fetch(`${API_BASE_URL}/get_features`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // data.categories: { "Ekran": ["ekran_..."], ... }
      console.log("Kategoriler alındı:", data.categories);
      return data.categories;
    } catch (error) {
      console.error("Kategorileri alırken hata:", error);
      throw error;
    }
  }

  // Tahmin yap
  static async predictPrice(inputData) {
    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(inputData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      return data.predicted_price;
    } catch (error) {
      console.error("Tahmin yaparken hata:", error);
      throw error;
    }
  }
}
