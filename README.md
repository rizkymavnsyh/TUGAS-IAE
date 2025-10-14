# API Marketplace dengan JWT

Dokumentasi ini menyediakan panduan lengkap untuk setup, konfigurasi, dan pengujian API Marketplace yang diamankan menggunakan otentikasi **JWT**.

---

## 1\. Cara Setup Environment & Menjalankan Server

### 1.1 Instalasi Dependensi

Pastikan sudah memiliki **Python** dan **pip** terinstal. Kemudian, instal semua pustaka yang dibutuhkan dari `requirements.txt`.

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

Buat file `.env` di direktori utama dan isi dengan variabel berikut. Ganti nilai placeholder dengan data ini.

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

Variabel berikut harus ada di dalam file `.env`:

- `JWT_SECRET`: Kunci rahasia yang digunakan untuk menandatangani token JWT.
- `PORT`: Port tempat server akan berjalan.
- `DB_HOST`: Host dari database MySQL.
- `DB_USER`: Nama pengguna untuk database MySQL.
- `DB_PASSWORD`: Kata sandi untuk database MySQL.
- `DB_NAME`: Nama database MySQL.

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
    - Untuk menyimpan token secara otomatis, buka tab **Scripts** lalu pilih Post-response dan tambahkan:
      ```javascript
      const data = pm.response.json();
      pm.collectionVariables.set('jwt_token', data.access_token);
      pm.collectionVariables.set('refresh_token', data.refresh_token);
      ```

2.  **Request Refresh Token**:

    - Buat request baru: `POST http://localhost:5000/auth/refresh`.
    - Buka tab **Body**, pilih **raw** dan **JSON**, lalu masukkan:
      ```json
      {
        "refresh_token": "{{refresh_token}}"
      }
      ```
    - Untuk memperbarui _access token_ secara otomatis, tambahkan skrip berikut di tab **Scripts** lalu pilih Post-response:
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

### 1. **Refresh Token (Invalid)**

#### Request:

- Method: `POST`
- Endpoint: `http://localhost:5000/auth/refresh`

**Body**:

```json
{
  "refresh_token": "This is not refresh_token"
}
```

#### Response (Error - 401):

```json
{
  "error": "Refresh token is invalid"
}
```

**Screenshot**:
<img width="1918" height="1020" alt="refresh token gagal" src="https://github.com/user-attachments/assets/f70f4919-9487-42f9-865b-6f048c8a522f" />


---

### 2. **Update Profile (User Not Found)**

#### Request:

- Method: `PUT`
- Endpoint: `http://localhost:5000/profile`

**Body**:

```json
{
  "name": "Nama Baru Dari Postman",
  "email": "new.email1@example.com"
}
```

#### Response (Error - 404):

```json
{
  "error": "User not found"
}
```

**Screenshot**:
<img width="1918" height="1021" alt="Update Profile User Not Found" src="https://github.com/user-attachments/assets/f51bbcfc-1863-4293-8c3d-64141ca6b243" />


---

### 3. **Update Profile (Token Invalid)**

#### Request:

- Method: `PUT`
- Endpoint: `http://localhost:5000/profile`

**Body**:

```json
{
  "name": "Nama Baru Dari Postman",
  "email": "new.email1@example.com"
}
```

#### Response (Error - 401):

```json
{
  "error": "Token is invalid"
}
```

**Screenshot**:
<img width="1918" height="1020" alt="Update Profile Token Invalid" src="https://github.com/user-attachments/assets/a40e3110-c3ec-4979-bc60-fffd5e77cba8" />


---

### 4. **Update Profile (Role Admin Denied)**

#### Request:

- Method: `PUT`
- Endpoint: `http://localhost:5000/profile`

**Body**:

```json
{
  "name": "Nama Baru Dari Postman",
  "email": "new.email1@example.com"
}
```

#### Response (Error - 403):

```json
{
  "error": "Permission denied"
}
```

**Screenshot**:
<img width="1918" height="1017" alt="Update Profile Role Admin Gagal" src="https://github.com/user-attachments/assets/0273aa47-99c5-4cd2-9bf6-cea85da375c0" />


---

### 5. **Login User (Invalid Credentials)**

#### Request:

- Method: `POST`
- Endpoint: `http://localhost:5000/auth/login`

**Body**:

```json
{
  "email": "user1@example.com",
  "password": "pass123"
}
```

#### Response (Error - 401):

```json
{
  "error": "Invalid credentials"
}
```

**Screenshot**:
<img width="1918" height="1017" alt="Login error 401" src="https://github.com/user-attachments/assets/64225fe8-2568-499c-81bf-f7c4fb28503f" />


---

### 6. **Update Profile (Successful)**

#### Request:

- Method: `PUT`
- Endpoint: `http://localhost:5000/profile`

**Body**:

```json
{
  "name": "Nama Baru Dari Postman",
  "email": "new.email@example.com"
}
```

#### Response (Success - 200):

```json
{
  "message": "Profile updated",
  "profile": {
    "email": "new.email@example.com",
    "name": "Nama Baru Dari Postman"
  }
}
```

**Screenshot**:
<img width="1918" height="1021" alt="Update Profile Berhasil" src="https://github.com/user-attachments/assets/8062e400-07e7-4353-a0b1-faa2c9d79f26" />


---

### 7. **Get Items (Successful)**

#### Request:

- Method: `GET`
- Endpoint: `http://localhost:5000/items`

#### Response (Success - 200):

```json
{
  "items": [
    {
      "id": 1,
      "name": "Item 1",
      "price": 12345
    },
    {
      "id": 2,
      "name": "Item 2",
      "price": 67890
    }
  ]
}
```

**Screenshot**:
<img width="1918" height="1017" alt="Get Items Berhasil" src="https://github.com/user-attachments/assets/07e8892b-43f6-4f24-b3b2-e11c12dff8b6" />

---

### 8. **Refresh Token (Successful)**

#### Request:

- Method: `POST`
- Endpoint: `http://localhost:5000/auth/refresh`

**Body**:

```json
{
  "refresh_token": "{{refresh_token}}"
}
```

#### Response (Success - 200):

```json
{
  "access_token": "<new_valid_token>"
}
```

**Screenshot**:
<img width="1918" height="1017" alt="refresh token berhasil" src="https://github.com/user-attachments/assets/50468d8d-9702-4581-a0f9-bf550c1485d0" />


---

### 9. **Login User (Successful)**

#### Request:

- Method: `POST`
- Endpoint: `http://localhost:5000/auth/login`

**Body**:

```json
{
  "email": "user1@example.com",
  "password": "pass123"
}
```

#### Response (Success - 200):

```json
{
  "access_token": "<JWT>",
  "refresh_token": "<Refresh JWT>"
}
```

**Screenshot**:
<img width="1918" height="1015" alt="Login berhasil" src="https://github.com/user-attachments/assets/ea9a4c59-b74d-480b-ab1c-fd8018cf0be8" />


## 7\. Contoh cURL

### 1. **Refresh Token (Invalid) Request**

```bash
curl --request POST --url http://localhost:5000/auth/refresh --header "Content-Type: application/json" --data "{\"refresh_token\": \"This is not refresh_token\"}"
```

**Screenshot**:
<img width="1898" height="80" alt="refresh token 401" src="https://github.com/user-attachments/assets/fac9e110-8d36-49ab-b6fb-f136c73b22d5" />


### 2. **Update Profile (User Not Found) Request**

```bash
curl --request PUT --url http://localhost:5000/profile --header "Content-Type: application/json" --data "{\"name\": \"Nama Baru Dari Postman\", \"email\": \"new.email1@example.com\"}"
```
**Screenshot**:
<img width="1886" height="137" alt="Update Profile 404" src="https://github.com/user-attachments/assets/8cb5c53d-e95c-4249-9d09-f7a83600d650" />


### 3. **Update Profile (Token Invalid) Request**

```bash
curl --request PUT --url http://localhost:5000/profile --header "Content-Type: application/json" --header "Authorization: Bearer <your_invalid_token>" --data "{\"name\": \"Nama Baru Dari Postman\", \"email\": \"new.email1@example.com\"}"
```
**Screenshot**:
<img width="1897" height="121" alt="Update Profile 401" src="https://github.com/user-attachments/assets/ef077a3d-e045-493c-a201-caff7ce8b126" />


### 4. **Update Profile (Permission Denied) Request**

```bash
curl --request PUT --url http://localhost:5000/profile --header "Content-Type: application/json" --header "Authorization: Bearer <your_admin_token>" --data "{\"name\": \"Nama Baru Dari Postman\", \"email\": \"new.email1@example.com\"}"
```
**Screenshot**:
<img width="1892" height="132" alt="Update Profile 403" src="https://github.com/user-attachments/assets/32353a2d-5791-4392-a371-19752285a44a" />


### 5. **Login User (Invalid Credentials) Request**

```bash
curl --request POST --url http://localhost:5000/auth/login --header "Content-Type: application/json" --data "{\"email\": \"user1@example.com\", \"password\": \"pass123\"}"
```
**Screenshot**:
<img width="1888" height="85" alt="Login user 401" src="https://github.com/user-attachments/assets/04c3cd69-bbbb-41c9-8ab9-f9bcf521947e" />


### 6. **Update Profile (Successful) Request**

```bash
curl --request PUT --url http://localhost:5000/profile --header "Content-Type: application/json" --header "Authorization: Bearer <your_valid_token>" --data "{\"name\": \"Nama Baru Dari Postman\", \"email\": \"new.email1@example.com\"}"
```
**Screenshot**:
<img width="1886" height="127" alt="Update Profile 200" src="https://github.com/user-attachments/assets/eb2511b8-ee2e-4c51-b9c0-942e928b0d7c" />


### 7. **Get Items (Successful) Request**

```bash
curl --request GET --url http://localhost:5000/items --header "Authorization: Bearer <your_valid_token>"
```
**Screenshot**:
<img width="1890" height="103" alt="Get items 200" src="https://github.com/user-attachments/assets/b4f6be85-9297-4195-9b40-df2a373d27a4" />


### 8. **Refresh Token (Successful) Request**

```bash
curl --request POST --url http://localhost:5000/auth/refresh --header "Content-Type: application/json" --data "{\"refresh_token\": \"<your_valid_refresh_token>\"}"
```
**Screenshot**:
<img width="1886" height="127" alt="refresh token 200" src="https://github.com/user-attachments/assets/0575995b-7cba-4cce-b727-6a2a1af9f233" />


### 9. **Login User (Successful) Request**

```bash
curl --request POST --url http://localhost:5000/auth/login --header "Content-Type: application/json" --data "{\"email\": \"user1@example.com\", \"password\": \"pass123\"}"
```
**Screenshot**:
<img width="1890" height="128" alt="Login user 200" src="https://github.com/user-attachments/assets/d0db068b-dac9-4b64-b1a5-5f7c391c77fe" />


## 8\. Catatan Kendala/Asumsi

- **Token Expiry**: Token akses berlaku selama 15 menit dan dapat diperbarui menggunakan **refresh token** yang berlaku selama 7 hari.
- **Role-based Access**: Fitur akses berbasis peran (`role`) sudah diterapkan. Hanya pengguna dengan **role "user"** yang dapat mengakses endpoint `/profile`.
- **Swagger UI**: Untuk dokumentasi API, dapat diakses melalui `http://localhost:5000/swagger`.
- **Database**: Proyek ini dikonfigurasi untuk menggunakan MySQL. Pastikan server MySQL sedang berjalan.
- **Keamanan**: Kata sandi disimpan menggunakan hash. Jangan pernah menyimpan kata sandi sebagai teks biasa di produksi.
