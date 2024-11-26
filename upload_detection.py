import joblib
from common_utils import UPLOAD_FOLDER, FEATURES_FILE, extract_file_features

# Đường dẫn file model
MODEL_FILE = "attack_detection_model.pkl"

# Tải mô hình và vectorizer
model_data = joblib.load(MODEL_FILE)
model = model_data["model"]
vectorizer = model_data["vectorizer"]

def predict_attack(file_features):
    """
    Sử dụng mô hình học máy để dự đoán file có khả năng bị tấn công không.
    :param file_features: Đặc trưng của file (dictionary).
    :return: True nếu file có khả năng bị tấn công, False nếu an toàn.
    """
    # Chuẩn bị đặc trưng để dự đoán
    size = file_features["size"]
    contains_exec = int(file_features["contains_exec"])
    keywords = ", ".join(file_features["detected_keywords"])

    # Vector hóa từ khóa
    keywords_vector = vectorizer.transform([keywords]).toarray()

    # Tạo vector đặc trưng đầy đủ
    feature_vector = [size, contains_exec] + list(keywords_vector[0])

    # Dự đoán
    prediction = model.predict([feature_vector])[0]
    return prediction == 1  # Trả về True nếu dự đoán là tấn công
