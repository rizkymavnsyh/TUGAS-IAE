# API Marketplace dengan JWT

Dokumentasi ini menyediakan panduan lengkap untuk setup, konfigurasi, dan pengujian API Marketplace yang diamankan menggunakan otentikasi **JWT**.

---

## 1\. Cara Setup Environment & Menjalankan Server

### 1.1 Instalasi Dependensi

Pastikan Anda memiliki **Python** dan **pip** terinstal. Kemudian, instal semua pustaka yang dibutuhkan dari `requirements.txt`.

1.  Buat dan aktifkan **virtual environment** (direkomendasikan):
    ```bash
    python -m venv venv
    ```
    **Windows:**
    ```bash
    venv\Scripts\Activate
    ```
    **macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```
2.  Instal dependensi:
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

Server akan berjalan di [http://localhost:5000](https://www.google.com/search?q=http://localhost:5000).

---

## 2\. Variabel Environment yang Diperlukan

Variabel berikut harus ada di dalam file `.env` Anda:

- `JWT_SECRET`: Kunci rahasia yang digunakan untuk menandatangani token JWT.
- `PORT`: Port tempat server akan berjalan.
- `DB_HOST`: Host dari database MySQL Anda.
- `DB_USER`: Nama pengguna untuk database MySQL Anda.
- `DB_PASSWORD`: Kata sandi untuk database MySQL Anda.
- `DB_NAME`: Nama database MySQL Anda.

---

## 3\. Peran Pengguna (User Roles)

Aplikasi ini memiliki dua jenis peran pengguna dengan hak akses yang berbeda.

| **Peran** | **Deskripsi**                                                                                                  | **Kredensial Demo**                          |
| --------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| user      | Peran standar untuk pengguna. Dapat melihat item dan memperbarui profil sendiri.                               | email: `user1@example.com`, pass: `pass123`  |
| admin     | Peran untuk administrator. Memiliki hak akses yang berbeda dan tidak dapat mengakses endpoint profil pengguna. | email: `admin@example.com`, pass: `admin123` |

---

## 4\. Daftar Endpoint

| **Method** | **Endpoint**  | **Keamanan** | **Deskripsi**                              |
| ---------- | ------------- | ------------ | ------------------------------------------ |
| POST       | /auth/login   | Publik       | Login untuk mendapatkan token JWT.         |
| POST       | /auth/refresh | Publik       | Memperbarui access token yang kedaluwarsa. |
| GET        | /items        | Publik       | Mendapatkan daftar item marketplace.       |
| PUT        | /profile      | JWT          | Memperbarui profil pengguna (hanya user).  |

---

## 5\. Panduan Pengujian API

### 5.1 Menggunakan Postman

Cocok untuk pengujian yang lebih kompleks dan berulang.

1.  **Request Login**:

    - Buat request baru: `POST http://localhost:5000/auth/login`.
    - Buka tab **Body**, pilih **raw** dan **JSON**, lalu masukkan kredensial:
      ```json
      {
        "email": "user1@example.com",
        "password": "pass123"
      }
      ```
    - Untuk menyimpan token secara otomatis, buka tab **Tests** dan tambahkan:
      ```javascript
      const data = pm.response.json();
      pm.collectionVariables.set('jwt_token', data.access_token);
      ```

2.  **Request Refresh Token**:

    - Buat request baru: `POST http://localhost:5000/auth/refresh`.
    - Buka tab **Body**, pilih **raw** dan **JSON**, lalu masukkan:
      ```json
      {
        "refresh_token": "{{refresh_token}}"
      }
      ```
    - Untuk memperbarui _access token_ Anda secara otomatis, tambahkan skrip berikut di tab **Tests**:
      ```javascript
      const data = pm.response.json();
      pm.collectionVariables.set('jwt_token', data.access_token);
      ```

3.  **Request Get Items**:

    - Buat request baru: `GET http://localhost:5000/items`.
    - Tidak perlu otorisasi atau body. Kirim request.

4.  **Request Update Profile**:

    - Buat request baru: `PUT http://localhost:5000/profile`.
    - Buka tab **Authorization**, pilih **Bearer Token**, dan masukkan `{{jwt_token}}` di kolom Token.
    - Buka tab **Body**, pilih **raw** dan **JSON**, lalu masukkan data profil yang ingin diubah.
    - Kirim request.

---

## 6\. Daftar Endpoint + Skema Request/Response

### 1\. **POST `/auth/login`**

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

### 2\. **POST `/auth/refresh`**

Endpoint ini digunakan untuk merefresh token sebelumnya.

**Request:**

```json
{
  "refresh_token": "<Refresh JWT>"
}
```

**Response (Sukses - 200):**

```json
{
  "access_token": "<New JWT>"
}
```

**Response (Error - 401):**

```json
{
  "error": "Refresh token expired"
}
```

### 3\. **GET `/items`** (Publik)

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

### 4\. **PUT `/profile`** (Terproteksi - JWT)

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

**Response (Error - 404):**

```json
{
  "error": "User not found"
}
```

---

## 7\. Contoh cURL

### 1\. **Login dan Dapatkan JWT**

```bash
curl -s -X POST http://localhost:5000/auth/login   -H "Content-Type: application/json"   -d '{"email":"user1@example.com","password":"pass123"}'
```

### 2\. **Gunakan Refresh Token untuk Mendapatkan Token Baru**

```bash
curl -s -X POST http://localhost:5000/auth/refresh   -H "Content-Type: application/json"   -d "{"refresh_token":"$REFRESH_TOKEN"}" | jq -r .access_token)
```

### 3\. **Akses Daftar Item Marketplace (Publik)**

```bash
curl -s http://localhost:5000/items
```

### 4\. **Update Profil Pengguna (Dengan JWT)**

```bash
TOKEN="<paste_JWT_from_login>"
curl -s -X PUT http://localhost:5000/profile   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{"name":"Updated Name"}'
```

---

## 8\. Catatan Kendala/Asumsi

- **Token Expiry**: Token akses berlaku selama 15 menit dan dapat diperbarui menggunakan **refresh token** yang berlaku selama 7 hari.
- **Role-based Access**: Fitur akses berbasis peran (`role`) sudah diterapkan. Hanya pengguna dengan **role "user"** yang dapat mengakses endpoint `/profile`.
- **Swagger UI**: Untuk dokumentasi API, dapat diakses melalui `http://localhost:5000/swagger`.
- **Database**: Proyek ini dikonfigurasi untuk menggunakan MySQL. Pastikan server MySQL Anda berjalan.
- **Keamanan**: Kata sandi disimpan menggunakan hash. Jangan pernah menyimpan kata sandi sebagai teks biasa di produksi.
