import os

# Đường dẫn để lưu file upload và log đặc trưng
UPLOAD_FOLDER = "uploaded_files"
FEATURES_FILE = "file_features.txt"

# Tạo thư mục nếu chưa tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def extract_file_features(file_path):
    """
    Phân tích đặc trưng file:
    - Đuôi file
    - Dung lượng file
    - Có chứa lệnh thực thi không
    - Liệt kê các từ khóa nguy hiểm xuất hiện
    """
    features = {}
    file_extension = os.path.splitext(file_path)[1].lower().strip(".")
    features["extension"] = file_extension

    # Loại bỏ các file không đáng phân tích
    non_executable_extensions = ["png", "jpg", "jpeg", "gif", "bmp", "tiff", "ico"]
    if file_extension in non_executable_extensions:
        features["contains_exec"] = False
        features["detected_keywords"] = []
        return features

    file_size = os.path.getsize(file_path)  # Dung lượng file (bytes)
    features["size"] = file_size

    # Kiểm tra nội dung file có chứa lệnh thực thi không và liệt kê từ khóa
    with open(file_path, "rb") as f:
        content = f.read().decode(errors="ignore")  # Đọc nội dung file

        # Danh sách từ khóa nguy hiểm
        dangerous_keywords = [
            # PHP
            "exec", "shell_exec", "system", "passthru", "eval", "assert",
            # Node.js
            "require", "import", "process.env", "child_process", "os.system",
            "spawn", "execFile", "eval", "Function", "setTimeout", "setInterval",
            "process.exit",
            # Bash/Unix shell commands
            "mv", "cp", "chmod", "chown", "kill", "ps", "top",
            # Batch/Command shell (Windows)
            "del", "rd", "rmdir", "taskkill", "shutdown", "start", "copy", "move",
            # Dangerous behavior
            "mkfs", "dd", "nc -e", "exec 5<>"
        ]

        # Kiểm tra sự xuất hiện của các từ khóa
        detected_keywords = [keyword for keyword in dangerous_keywords if keyword in content.lower()]
        features["contains_exec"] = len(detected_keywords) > 0  # True nếu có từ khóa nguy hiểm
        features["detected_keywords"] = detected_keywords  # Liệt kê các từ khóa phát hiện được

    return features
