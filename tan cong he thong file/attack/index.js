const fs = require('fs');
const axios = require('axios');

const filePath = './exploit.js'; 
const fileStream = fs.createReadStream(filePath);

const url = 'http://localhost:3000/upload';

const FormData = require('form-data');
const form = new FormData();
form.append('file', fileStream, 'exploit.js');

axios.post(url, form, {
  headers: {
    ...form.getHeaders() 
  }
}).then(response => {
  console.log('Response:', response.data); 
}).catch(error => {
  console.error('Lỗi:', error);
});
