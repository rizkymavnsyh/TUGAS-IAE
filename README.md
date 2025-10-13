# API Marketplace dengan JWT

## 1. Cara Setup Environment & Menjalankan Server

1. **Instalasi Dependensi**:
   
   Pertama, pastikan Anda telah menginstal dependensi yang dibutuhkan dengan perintah berikut:

   ```bash
   pip install -r requirements.txt
   ```

2. **Konfigurasi .env**:
   
   Buat file `.env` di direktori root proyek dan masukkan variabel berikut:
   
   ```bash
   JWT_SECRET=your_secret_here
   PORT=5000
   ```

   Gantilah `your_secret_here` dengan kunci rahasia yang Anda inginkan.

3. **Menjalankan Server**:

   Setelah semua dependensi terinstal dan konfigurasi selesai, jalankan aplikasi Flask dengan perintah:

   ```bash
   python app.py
   ```

   Server akan berjalan di `http://localhost:5000`.

---

## 2. Variabel Environment yang Diperlukan

- `JWT_SECRET`: Kunci rahasia untuk menandatangani token JWT.
- `PORT`: Port tempat server akan dijalankan (default: `5000`).

---

## 3. Daftar Endpoint + Skema Request/Response

### 1. **POST `/auth/login`**

Endpoint ini digunakan untuk login dan mendapatkan token JWT.

**Request:**
```json
{
  "email": "user1@example.com",
  "password": "pass123"
}
```

**Response (Sukses - 200):**
```json
{
  "access_token": "<JWT>",
  "refresh_token": "<Refresh JWT>"
}
```

**Response (Error - 401):**
```json
{
  "error": "Invalid credentials"
}
```

---

### 2. **GET `/items`** (Publik)

Endpoint ini mengembalikan daftar item marketplace yang dapat diakses tanpa autentikasi.

**Response (Sukses - 200):**
```json
{
  "items": [
    { "id": 1, "name": "Item 1", "price": 12345 },
    { "id": 2, "name": "Item 2", "price": 67890 }
  ]
}
```

---

### 3. **PUT `/profile`** (Terproteksi - JWT)

Endpoint ini digunakan untuk memperbarui profil pengguna. Harus menggunakan JWT yang valid di header Authorization.

**Request:**
```json
{
  "name": "Updated Name",
  "email": "updated@example.com"
}
```

**Response (Sukses - 200):**
```json
{
  "message": "Profile updated",
  "profile": {
    "name": "Updated Name",
    "email": "updated@example.com"
  }
}
```

**Response (Error - 401):**
```json
{
  "error": "Invalid token"
}
```

**Response (Error - 403):**
```json
{
  "error": "Permission denied"
}
```

---

## 4. Contoh cURL (Wajib) atau Postman (Koleksi Diekspor)

### 1. **Login dan Dapatkan JWT**

```bash
curl -s -X POST http://localhost:5000/auth/login   -H "Content-Type: application/json"   -d '{"email":"user1@example.com","password":"pass123"}'
```

Output yang akan diterima:
```json
{
  "access_token": "<JWT>",
  "refresh_token": "<Refresh JWT>"
}
```

### 2. **Akses Daftar Item Marketplace (Publik)**

```bash
curl -s http://localhost:5000/items
```

Output yang akan diterima:
```json
{
  "items": [
    { "id": 1, "name": "Item 1", "price": 12345 },
    { "id": 2, "name": "Item 2", "price": 67890 }
  ]
}
```

### 3. **Update Profil Pengguna (Dengan JWT)**

```bash
TOKEN="<paste_JWT_from_login>"
curl -s -X PUT http://localhost:5000/profile   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{"name":"Updated Name"}'
```

Output yang akan diterima:
```json
{
  "message": "Profile updated",
  "profile": {
    "name": "Updated Name",
    "email": "updated@example.com"
  }
}
```

---

## 5. Catatan Kendala/Asumsi (Jika Ada)

- **Penggunaan Data Dummy**: Dalam implementasi ini, data pengguna seperti email dan password adalah data dummy yang disimpan di dalam memori.
- **Token Expiry**: Token akses berlaku selama 15 menit dan dapat diperbarui menggunakan **refresh token**.
- **Role-based Access**: Fitur akses berbasis peran (`role`) sudah diterapkan. Hanya pengguna dengan **role "user"** yang dapat mengakses endpoint `/profile`.
- **Swagger UI**: Untuk dokumentasi API, dapat diakses melalui `http://localhost:5000/swagger`.

---

Dengan ini, **README.md** Anda sudah memenuhi kriteria yang diminta dalam instruksi tugas. Jika Anda ingin menambahkan **Postman Collection** atau **screenshot uji**, beri tahu saya, dan saya akan membantu Anda menambahkannya!
