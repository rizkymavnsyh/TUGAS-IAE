# API Marketplace dengan JWT

Dokumentasi ini menyediakan panduan lengkap untuk setup, konfigurasi, dan pengujian API Marketplace yang diamankan menggunakan otentikasi **JWT**.

## 1. Persiapan Lingkungan

### 1.1 Instalasi Dependensi

Pastikan Anda memiliki **Python** dan **pip** terinstal. Kemudian, instal semua pustaka yang dibutuhkan dari `requirements.txt`.

1. Buat dan aktifkan **virtual environment** (direkomendasikan):

   ```bash
   python -m venv venv
   venv\Scripts\Activate di Windows atau source venv/bin/activate di mac
   ```

2. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```

### 1.2 Konfigurasi Environment

Buat file `.env` di direktori utama dan isi dengan variabel berikut. Ganti nilai placeholder dengan data Anda.

```ini
# Kunci rahasia untuk JWT
JWT_SECRET=your_super_secret_key

# Port server
PORT=5000

# Variabel untuk koneksi database MySQL
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=flask_api
```

### 1.3 Inisialisasi Database

Sebelum menjalankan server, pastikan database dan tabel sudah dibuat. Jalankan skrip ini sekali saja:

```bash
python init_db.py
```

### 1.4 Menjalankan Server

Setelah semua persiapan selesai, jalankan server aplikasi:

```bash
python app.py
```

Server akan berjalan di [http://localhost:5000](http://localhost:5000).

## 2. Peran Pengguna (User Roles)

Aplikasi ini memiliki dua jenis peran pengguna dengan hak akses yang berbeda.

| **Peran** | **Deskripsi**                                                                                                  | **Kredensial Demo**                          |
| --------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| user      | Peran standar untuk pengguna. Dapat melihat item dan memperbarui profil sendiri.                               | email: `user1@example.com`, pass: `pass123`  |
| admin     | Peran untuk administrator. Memiliki hak akses yang berbeda dan tidak dapat mengakses endpoint profil pengguna. | email: `admin@example.com`, pass: `admin123` |

## 3. Daftar Endpoint

| **Method** | **Endpoint**  | **Keamanan** | **Deskripsi**                              |
| ---------- | ------------- | ------------ | ------------------------------------------ |
| POST       | /auth/login   | Publik       | Login untuk mendapatkan token JWT.         |
| POST       | /auth/refresh | Publik       | Memperbarui access token yang kedaluwarsa. |
| GET        | /items        | Publik       | Mendapatkan daftar item marketplace.       |
| PUT        | /profile      | JWT          | Memperbarui profil pengguna (hanya user).  |

## 4. Panduan Pengujian API

### 4.1 Menggunakan Swagger UI (Interaktif)

Cara termudah untuk mencoba API secara visual.

1. **Buka Dokumentasi**: Setelah server berjalan, buka [http://localhost:5000/swagger](http://localhost:5000/swagger) di browser Anda.

2. **Login**:

   - Buka endpoint `POST /auth/login`.
   - Klik "Try it out".
   - Masukkan JSON berikut di Request body:
     ```json
     {
       "email": "user1@example.com",
       "password": "pass123"
     }
     ```
   - Klik "Execute". Salin `access_token` dari respons.

3. **Get Items (Publik)**:

   - Buka endpoint `GET /items`.
   - Klik "Try it out".
   - Klik "Execute". Anda akan melihat daftar item di respons.

4. **Otorisasi**:

   - Klik tombol hijau "Authorize" di bagian atas halaman.
   - Di dalam popup, tempelkan token yang sudah Anda salin dengan format `Bearer <token_anda>`.
   - Klik "Authorize" lalu "Close".

5. **Akses Endpoint Terproteksi**:
   - Sekarang, coba buka endpoint `PUT /profile`.
   - Klik "Try it out" dan masukkan data baru di Request body.
   - Klik "Execute". Permintaan akan berhasil karena Anda menggunakan token user.

### 4.2 Menggunakan Postman

Cocok untuk pengujian yang lebih kompleks dan berulang.

1. **Request Login**:

   - Buat request baru: `POST http://localhost:5000/auth/login`.
   - Buka tab Body, pilih raw dan JSON, lalu masukkan kredensial.
   - Untuk menyimpan token secara otomatis, buka tab Tests dan tambahkan:
     ```javascript
     const data = pm.response.json();
     pm.collectionVariables.set('jwt_token', data.access_token);
     ```

2. **Request Get Items**:

   - Buat request baru: `GET http://localhost:5000/items`.
   - Tidak perlu otorisasi atau body.
   - Kirim request.

3. **Request Update Profile**:
   - Buat request baru: `PUT http://localhost:5000/profile`.
   - Buka tab Authorization, pilih Bearer Token, dan masukkan `{{jwt_token}}` di kolom Token.
   - Buka tab Body, pilih raw dan JSON, lalu masukkan data profil yang ingin diubah.
   - Kirim request.

### 4.3 Menggunakan cURL (Terminal)

Untuk pengujian cepat dari command line.

1. **Login (Simpan Token)**:

   - Untuk Windows (CMD/PowerShell):

     ```bash
     curl -s -X POST http://localhost:5000/auth/login -H "Content-Type: application/json" -d "{"email":"user1@example.com","password":"pass123"}"
     ```

   - Untuk Linux/macOS:
     ```bash
     TOKEN=$(curl -s -X POST http://localhost:5000/auth/login         -H "Content-Type: application/json"         -d '{"email":"user1@example.com","password":"pass123"}' | jq -r .access_token)
     ```

2. **Get Items (Publik)**:

   ```bash
   curl -s http://localhost:5000/items
   ```

3. **Update Profile (Gunakan Token)**:
   - Ganti `<TOKEN_ANDA>` dengan token dari langkah sebelumnya:
     ```bash
     curl -s -X PUT http://localhost:5000/profile -H "Authorization: Bearer <TOKEN_ANDA>" -H "Content-Type: application/json" -d "{"name":"Nama Baru via cURL"}"
     ```
---

## 5. Daftar Endpoint + Skema Request/Response

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

## 6. Contoh cURL (Wajib) atau Postman (Koleksi Diekspor)

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

## 7. Catatan Kendala/Asumsi (Jika Ada)

- **Token Expiry**: Token akses berlaku selama 15 menit dan dapat diperbarui menggunakan **refresh token** yang berlaku selama 7 hari.
- **Role-based Access**: Fitur akses berbasis peran (`role`) sudah diterapkan. Hanya pengguna dengan **role "user"** yang dapat mengakses endpoint `/profile`.
- **Swagger UI**: Untuk dokumentasi API, dapat diakses melalui `http://localhost:5000/swagger`.
- **Database**: Proyek ini dikonfigurasi untuk menggunakan MySQL. Pastikan server MySQL Anda berjalan.
- **Keamanan**: Kata sandi disimpan menggunakan hash. Jangan pernah menyimpan kata sandi sebagai teks biasa di produksi.

---
