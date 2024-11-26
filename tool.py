from mitmproxy import http
import os
import re
from common_utils import UPLOAD_FOLDER, FEATURES_FILE, extract_file_features
from upload_detection import predict_attack
from socket_client import send_to_nodejs  # Import hàm client từ file socket_client.py
def request(flow: http.HTTPFlow):
    """
    Hàm xử lý các request qua mitmproxy.
    """
    # Kiểm tra xem request có đến endpoint /upload không
    if flow.request.method == "POST" and "/upload" in flow.request.url:
        print("\n--- Detected File Upload Request ---")
        print(f"URL: {flow.request.url}")
        print(f"Headers: {flow.request.headers}")

        # Phân tích content để lấy file
        content_type = flow.request.headers.get("Content-Type", "")
        if "multipart/form-data" in content_type:
            # Trích xuất boundary từ Content-Type
            boundary = re.search(r'boundary=(.+)', content_type)
            if boundary:
                boundary = boundary.group(1)
                # Tách request content thành các phần dựa trên boundary
                parts = flow.request.content.split(boundary.encode())
                for part in parts:
                    # Tìm phần chứa file
                    if b"Content-Disposition" in part and b"filename=" in part:
                        # Lấy tên file từ header Content-Disposition
                        disposition = re.search(
                            b'filename="(.+?)"', part, re.IGNORECASE
                        )
                        if disposition:
                            file_name = disposition.group(1).decode()
                            # Lấy dữ liệu file
                            file_data = part.split(b"\r\n\r\n", 1)[1].rsplit(b"\r\n--", 1)[0]
                            # Lưu file vào thư mục UPLOAD_FOLDER
                            file_path = os.path.join(UPLOAD_FOLDER, file_name)
                            with open(file_path, "wb") as f:
                                f.write(file_data)
                            print(f"Saved uploaded file: {file_path}")

                            # Phân tích đặc trưng file
                            features = extract_file_features(file_path)
                            print(f"Extracted features: {features}")

                            # Sử dụng mô hình để dự đoán
                            is_attack = predict_attack(features)
                            print(f"Prediction: {'Attack detected' if is_attack else 'Safe file'}")

                            # Gửi dữ liệu qua socket
                            data_to_send = {
                                'file_name': file_name,
                                'is_attack': int(is_attack),
                            }
                            send_to_nodejs(data_to_send)  # Gửi dữ liệu qua socket

                            # Lưu đặc trưng vào file log
                            with open(FEATURES_FILE, "a", encoding="utf-8") as log_file:
                                log_file.write(f"File: {file_name}\n")
                                log_file.write(f"  Extension: {features['extension']}\n")
                                log_file.write(f"  Size: {features['size']} bytes\n")
                                log_file.write(f"  Contains executable commands: {features['contains_exec']}\n")
                                log_file.write(f"  Detected keywords: {', '.join(features['detected_keywords'])}\n")
                                log_file.write("\n")
        print("Request info and file features saved.")
