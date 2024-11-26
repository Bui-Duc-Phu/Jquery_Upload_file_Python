const express = require('express');
const multer = require('multer');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs');
const net = require('net');
const { exec } = require('child_process');

const app = express();
const hostname = "192.168.0.109"
const expressPort = 3001;
const socketPort = 3002;

const SECRET_CODE = '12345'; // Mã xác thực để kiểm tra

// Đường dẫn tới thư mục uploads
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

// Đường dẫn tới thư mục tạm
const tempUploadDir = path.join(__dirname, 'temp_uploads');
if (!fs.existsSync(tempUploadDir)) {
  fs.mkdirSync(tempUploadDir);
}

// Cấu hình multer để lưu file vào thư mục tạm
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, tempUploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname);
  },
});
const upload = multer({ storage: storage });

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Lưu trạng thái các file từ socket và trạng thái xác thực
const fileStatus = {}; // Lưu trạng thái từ socket (file_name -> is_attack)
const verifiedFiles = new Set(); // Lưu các file đã xác thực

// Socket server
const server = net.createServer((socket) => {
  let receivedData = Buffer.alloc(0);
  let expectedLength = null;

  socket.on('data', (chunk) => {
    if (expectedLength === null) {
      expectedLength = chunk.readInt32BE(0);
      chunk = chunk.slice(4);
    }

    receivedData = Buffer.concat([receivedData, chunk]);

    if (receivedData.length >= expectedLength) {
      try {
        const data = JSON.parse(receivedData.slice(0, expectedLength).toString('utf-8'));
        console.log('Received data:', data);

        // Lưu trạng thái file
        fileStatus[data.file_name] = data.is_attack;
      } catch (error) {
        console.error('Error parsing JSON:', error);
      }

      receivedData = Buffer.alloc(0);
      expectedLength = null;
    }
  });

  socket.on('error', (err) => {
    console.error('Socket error:', err);
  });
});

// Giao diện chính
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Route để hiển thị hộp thoại xác thực
app.get('/verify', (req, res) => {
  const fileName = req.query.file_name;
  res.send(`
    <html>
    <body>
      <h1>Phát hiện file không an toàn</h1>
      <p>Tên tệp: ${fileName}</p>
      <form action="/verify" method="post">
        <input type="hidden" name="file_name" value="${fileName}">
        <label for="code">Nhập mã xác thực:</label>
        <input type="text" id="code" name="code">
        <button type="submit">Xác thực</button>
      </form>
    </body>
    </html>
  `);
});

// Xử lý xác thực
app.post('/verify', (req, res) => {
  const { file_name, code } = req.body;

  if (code === SECRET_CODE) {
    console.log(`File "${file_name}" đã được xác thực.`);
    verifiedFiles.add(file_name); // Đánh dấu file đã xác thực

    // Chuyển file từ thư mục tạm sang thư mục chính thức
    const tempFilePath = path.join(tempUploadDir, file_name);
    const finalFilePath = path.join(uploadDir, file_name);

    fs.rename(tempFilePath, finalFilePath, (err) => {
      if (err) {
        console.error('Error moving file:', err);
        return res.status(500).send('Lỗi khi xử lý file sau khi xác thực.');
      }

      console.log(`File "${file_name}" đã được chuyển sang thư mục chính.`);
      // Thực thi file sau khi xác thực
      exec(`node ${JSON.stringify(finalFilePath)}`, (err, stdout, stderr) => {
        if (err) {
          console.error('Execution error:', err);
          return res.status(500).send('Lỗi khi thực thi file.');
        } else {
          console.log(`Output: ${stdout}`);
          // Quay lại giao diện chính với thông báo thành công
          return res.redirect('/?status=success');
        }
      });
    });
  } else {
    console.log(`Xác thực không thành công cho file "${file_name}".`);
    // Hiển thị lại giao diện nhập mã với thông báo lỗi
    res.send(`
      <html>
      <body>
        <h1>Phát hiện file không an toàn</h1>
        <p style="color: red;">Mã xác thực không đúng! Vui lòng thử lại.</p>
        <form action="/verify" method="post">
          <input type="hidden" name="file_name" value="${file_name}">
          <label for="code">Nhập mã xác thực:</label>
          <input type="text" id="code" name="code">
          <button type="submit">Xác thực</button>
        </form>
      </body>
      </html>
    `);
  }
});


// Route để xử lý upload
app.post('/upload', upload.single('file'), (req, res) => {
  const tempFilePath = path.join(tempUploadDir, req.file.originalname);
  const isAttack = fileStatus[req.file.originalname] || false;

  if (isAttack && !verifiedFiles.has(req.file.originalname)) {
    console.log(`File "${req.file.originalname}" cần xác thực trước khi upload.`);
    return res.redirect(`/verify?file_name=${req.file.originalname}`);
  }

  // Nếu file đã xác thực hoặc an toàn, chuyển file từ thư mục tạm sang thư mục chính thức
  const finalFilePath = path.join(uploadDir, req.file.originalname);
  fs.rename(tempFilePath, finalFilePath, (err) => {
    if (err) {
      console.error('Error moving file:', err);
      return res.status(500).send('Lỗi khi xử lý file.');
    }

    console.log(`File "${req.file.originalname}" đã được upload vào thư mục chính.`);
    exec(`node ${JSON.stringify(finalFilePath)}`, (err, stdout, stderr) => {
      if (err) {
        console.error('Execution error:', err);
        return res.redirect('/?status=success');
      } else {
        console.log(`Output: ${stdout}`);
        // Quay lại giao diện chính với thông báo thành công
        return res.redirect('/?status=success');
      }
    });
  });
});


// Lắng nghe Express và Socket server
app.listen(expressPort,hostname ,() => {
  console.log(`Express ứng dụng đang chạy tại http://${hostname}:${expressPort}`);
});

server.listen(socketPort,hostname,() => {
  console.log(`Socket server đang chạy tại ${hostname}:${socketPort}`);
});
