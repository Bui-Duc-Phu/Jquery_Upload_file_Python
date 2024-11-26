import tkinter as tk
from tkinter import messagebox
import subprocess

def run_tool():
    """
    Hàm mở PowerShell tại đường dẫn cụ thể và chạy lệnh mitmproxy.
    """
    try:
        # Đường dẫn nơi chứa tool.py
        tool_directory = r"D:\python\bai5"

        # Câu lệnh cần thực thi
        command = "mitmproxy -s tool.py --mode reverse:http://localhost:3001 --listen-port 3000"

        # Mở PowerShell và chạy lệnh
        subprocess.Popen(
            ["powershell", "-NoExit", f"cd {tool_directory}; {command}"],
            shell=True
        )

        # Hiển thị thông báo thành công
        messagebox.showinfo("Thông báo", "Tool.py đã được kích hoạt qua PowerShell!")
    except Exception as e:
        # Hiển thị thông báo lỗi
        messagebox.showerror("Lỗi", f"Không thể kích hoạt Tool.py:\n{e}")

def quit_app():
    """
    Hàm thoát ứng dụng.
    """
    if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn thoát không?"):
        root.destroy()

# Tạo giao diện chính
root = tk.Tk()
root.title("Mitmproxy Tool")
root.geometry("400x200")

# Tiêu đề
label = tk.Label(root, text="Kích hoạt Tool.py với Mitmproxy", font=("Arial", 14))
label.pack(pady=20)

# Nút kích hoạt tool.py
btn_run = tk.Button(root, text="Kích hoạt Tool.py", font=("Arial", 12), command=run_tool)
btn_run.pack(pady=10)

# Nút thoát
btn_exit = tk.Button(root, text="Thoát", font=("Arial", 12), command=quit_app)
btn_exit.pack(pady=10)

# Chạy giao diện
root.mainloop()
