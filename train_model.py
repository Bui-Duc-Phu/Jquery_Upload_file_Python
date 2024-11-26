import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Đường dẫn file đặc trưng
FEATURES_FILE = "file_features.txt"
MODEL_FILE = "attack_detection_model.pkl"

def load_features(file_path):
    data = {
        "extension": [],
        "size": [],
        "contains_exec": [],
        "keywords": [],
        "label": []
    }

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        current_keywords = []
        current_label = None

        for line in lines:
            try:
                line = line.strip()
                if line.startswith("File:"):
                    current_label = None  # Reset label
                elif line.startswith("Extension:"):
                    data["extension"].append(line.split(":")[1].strip())
                elif line.startswith("Size:"):
                    data["size"].append(int(line.split(":")[1].strip().split()[0]))
                elif line.startswith("Contains executable commands:"):
                    current_label = 1 if "True" in line else 0
                    data["contains_exec"].append(current_label)
                elif line.startswith("Detected keywords:"):
                    keywords = line.split(":")[1].strip()
                    current_keywords = keywords.split(", ") if keywords else []
                    data["keywords"].append(", ".join(current_keywords))
                    data["label"].append(current_label)
            except Exception as e:
                print(f"Skipping malformed line: {line}. Error: {e}")

    # Kiểm tra tính đồng bộ
    lengths = {key: len(value) for key, value in data.items()}
    if len(set(lengths.values())) != 1:
        raise ValueError(f"Inconsistent data lengths: {lengths}")

    return pd.DataFrame(data)



def preprocess_data(data):
    vectorizer = CountVectorizer()
    keywords_vectorized = vectorizer.fit_transform(data["keywords"])

    X = pd.concat([
        data[["size", "contains_exec"]],
        pd.DataFrame(keywords_vectorized.toarray(), columns=vectorizer.get_feature_names_out())
    ], axis=1)

    return X, vectorizer

def train_model(X, y):
    print("Label distribution:\n", y.value_counts())

    # Chia dữ liệu train/test, đảm bảo cân bằng nhãn bằng stratify
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Huấn luyện mô hình
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Đánh giá mô hình
    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Classification Report:\n", classification_report(y_test, y_pred))

    return model

def save_model(model, vectorizer):
    joblib.dump({"model": model, "vectorizer": vectorizer}, MODEL_FILE)
    print(f"Model saved to {MODEL_FILE}")

if __name__ == "__main__":
    print("Loading features...")
    data = load_features(FEATURES_FILE)

    print("Preprocessing data...")
    X, vectorizer = preprocess_data(data)
    y = data["label"]

    print("Training model...")
    model = train_model(X, y)

    print("Saving model...")
    save_model(model, vectorizer)
