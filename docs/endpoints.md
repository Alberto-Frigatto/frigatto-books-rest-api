# Endpoints

Below you'll see all API endpoints, separated by scope.

# Table of contents

- [Authentication](#authentication)
  - [Login](#login)
  - [Logout](#logout)
- [Book genres](#book-genres)
  - [Get all book genres](#get-all-book-genres)
  - [Get book genre by ID](#get-book-genre-by-id)
  - [Create book genre](#create-book-genre)
  - [Update book genre](#update-book-genre)
  - [Delete book genre](#delete-book-genre)
- [Book images](#book-images)
  - [Get book image by filename](#get-book-image-by-filename)
  - [Add image to a book](#add-image-to-a-book)
  - [Update book image](#update-book-image)
  - [Delete book image](#delete-book-image)
- [Book keywords](#book-keywords)
  - [Create book keyword](#create-book-keyword)
  - [Delete book keyword](#delete-book-keyword)
- [Book kinds](#book-kinds)
  - [Get all book kinds](#get-all-book-kinds)
  - [Get book kind by ID](#get-book-kind-by-id)
  - [Create book kind](#create-book-kind)
  - [Update book kind](#update-book-kind)
  - [Delete book kind](#delete-book-kind)
- [Books](#books)
  - [Get all books](#get-all-books)
  - [Get book by ID](#get-book-by-id)
  - [Create book](#create-book)
  - [Update book](#update-book)
  - [Delete book](#delete-book)
- [Saved books](#saved-books)
  - [Save a book](#save-a-book)
  - [Get all saved books](#get-all-saved-books)
  - [Delete saved book](#delete-saved-book)
- [Search](#search)
  - [Search books](#search-books)
- [Users](#users)
  - [Get user information](#get-user-information)
  - [Get user image by filename](#get-user-image-by-filename)
  - [Create user](#create-user)
  - [Update user](#update-user)
  - [Delete user](#delete-user)

<br/>

# Authentication

## Login

Authenticate the user in the system by its username and password.

### Request

`POST /auth/login`

#### Content-Type

- `application/json`

#### Payload fields

- `username` (String) - User's username
- `password` (String) - User's password


```bash
curl -i -X POST \
-H "Content-Type: application/json" \
-d '{
    "username": "String",
    "password": "String"
}' \
http://localhost:5000/auth/login
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 15:44:33 GMT
Content-Length: 115
Content-Type: application/json
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Set-Cookie: access_token_cookie=your_generated_access_token; Expires=Mon, 21 Jul 2025 16:51:13 GMT; Max-Age=31540000; Secure; HttpOnly; Path=/; SameSite=Strict
Set-Cookie: csrf_access_token=your_generated_csrf_token; Expires=Mon, 21 Jul 2025 16:51:13 GMT; Max-Age=31540000; Secure; Path=/; SameSite=Strict
Connection: close

{
    "id": 1,
    "img_url": "http://localhost:5000/users/photos/filename.jpg",
    "username": "String"
}
```

#### Response fields

- `id` (Number) - User's ID
- `img_url` (String) - User's image URL
- `username` (String) - User's username

### Possible errors

- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidContentType](./errors.md#invalidcontenttype)
- [InvalidDataSent](./errors.md#invaliddatasent)
- [InvalidLogin](./errors.md#invalidlogin)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [NoDataSent](./errors.md#nodatasent)
- [UserAlreadyAuthenticated](./errors.md#useralreadyauthenticated)

<br/>

## Logout

Expire the authentication cookies.

### Request

`GET /auth/logout`

```bash
curl -i -X GET http://localhost:5000/auth/logout
```

### Response `204 NO CONTENT`

```http
HTTP/1.1 204 NO CONTENT
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 16:25:29 GMT
Content-Type: application/json
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Set-Cookie: access_token_cookie=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Secure; HttpOnly; Path=/; SameSite=Strict
Set-Cookie: csrf_access_token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Secure; Path=/; SameSite=Strict
Set-Cookie: refresh_token_cookie=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Secure; HttpOnly; Path=/; SameSite=Strict
Set-Cookie: csrf_refresh_token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Secure; Path=/; SameSite=Strict
Connection: close
```

### Possible errors

- [DatabaseConnection](./errors.md#databaseconnection)
- [MethodNotAllowed](./errors.md#methodnotallowed)

<br/>

# Book genres

## Get all book genres

Get a pagination with all book genres.

### Request

`GET /bookGenres?page=<page>`

#### URL parameters

- (Optional) `page` (Number) - Page's number (if not provided, it'll be `1`)

```bash
curl -i -X GET http://localhost:5000/bookGenres?page=1
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 16:39:26 GMT
Content-Length: 186
Content-Type: application/json
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "data":[
        {
            "genre": "string",
            "id": 1
        }
    ],
    "has_next": false,
    "has_prev": false,
    "next_page": null,
    "page": 1,
    "per_page": 20,
    "prev_page": null,
    "total_items": 1,
    "total_pages": 1
}
```

#### Response fields

- `data` (Array) - Array with all book genres
  - `genre` (String) - Book genre's name
  - `id` (Number) - Book genre's ID
- `has_next` (Boolean) - Whether there's a next page
- `has_prev` (Boolean) - Whether there's a previous page
- `next_page` (Null | String) - Next page's URL if it exists (e.g. /bookGenres?page=2)
- `page` (Number) - Current page
- `per_page` (Number) - Total items for each page
- `prev_page` (Null | String) - Previous page's URL if it exists (e.g. /bookGenres?page=1)
- `total_items` (Number) - Total items returned
- `total_pages` (Number) - Total page quantity

### Possible errors

- [DatabaseConnection](./errors.md#databaseconnection)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [PaginationPageDoesntExist](./errors.md#paginationpagedoesntexist)

<br/>

## Get book genre by ID

Get a book genre by its ID.

### Request

`GET /bookGenres/<id>`

#### URL parameters

- `id` (Number) - Book genre's ID

```bash
curl -i -X GET http://localhost:5000/bookGenres/1
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 17:25:11 GMT
Content-Type: application/json
Content-Length: 52
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "genre": "string",
    "id": 1
}
```

#### Response fields

- `genre` (String) - Book genre's name
- `id` (Number) - Book genre's ID

### Possible errors

- [BookGenreDoesntExist](./errors.md#bookgenredoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [MethodNotAllowed](./errors.md#methodnotallowed)

<br/>

## Create book genre

Create a book genre providing its name.

### Request

`POST /bookGenres`

#### Content-Type

- `application/json`

#### Payload fields

- `genre` (String) - Book genre's name
  - Min length: `3`
  - Max length: `30`
  - Pattern: `^[a-zA-ZÀ-ÿç\s]+$` (Allows letters, spaces, and accented characters)

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X POST \
-H "Content-Type: application/json" \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
-d '{
    "genre": "String"
}' \
http://localhost:5000/bookGenres
```

### Response `201 CREATED`

```http
HTTP/1.1 201 CREATED
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 17:45:29 GMT
Content-Type: application/json
Content-Length: 26
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "genre": "string",
    "id": 1
}
```

#### Response fields

- `genre` (String) - Book genre's name (converted to lowercase and whitespace stripped)
- `id` (Number) - Book genre's ID

### Possible errors

- [BookGenreAlreadyExists](./errors.md#bookgenrealreadyexists)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidContentType](./errors.md#invalidcontenttype)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidDataSent](./errors.md#invaliddatasent)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)
- [NoDataSent](./errors.md#nodatasent)

<br/>

## Update book genre

Update a book genre by its ID providing its name.

### Request

`PATCH /bookGenres/<id>`

#### URL parameters

- `id` (Number) - Book genre's ID

#### Content-Type

- `application/json`

#### Payload fields

- `genre` (String) - Book genre's name
  - Min length: `3`
  - Max length: `30`
  - Pattern: `^[a-zA-ZÀ-ÿç\s]+$` (Allows letters, spaces, and accented characters)

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X PATCH \
-H "Content-Type: application/json" \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
-d '{
    "genre": "String"
}' \
http://localhost:5000/bookGenres/1
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 18:00:21 GMT
Content-Type: application/json
Content-Length: 29
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "genre": "string",
    "id": 1
}
```

#### Response fields

- `genre` (String) - Book genre's name (converted to lowercase and whitespace stripped)
- `id` (Number) - Book genre's ID

### Possible errors

- [BookGenreAlreadyExists](./errors.md#bookgenrealreadyexists)
- [BookGenreDoesntExist](./errors.md#bookgenredoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidContentType](./errors.md#invalidcontenttype)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidDataSent](./errors.md#invaliddatasent)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)
- [NoDataSent](./errors.md#nodatasent)

<br/>

## Delete book genre

Delete a book genre by its ID.

### Request

`DELETE /bookGenres/<id>`

#### URL parameters

- `id` (Number) - Book genre's ID

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X DELETE \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
http://localhost:5000/bookGenres/1
```

### Response `204 NO CONTENT`

```http
HTTP/1.1 204 NO CONTENT
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 18:42:55 GMT
Content-Type: application/json
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close
```

### Possible errors

- [BookGenreDoesntExist](./errors.md#bookgenredoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)
- [ThereAreLinkedBooksWithThisBookGenre](./errors.md#therearelinkedbookswiththisbookgenre)

<br/>

# Book images

## Get book image by filename

Retrieve the binary data of a book image based on its filename.

### Request

`GET /books/photos/<filename>`

#### URL parameters

- `filename` (String) - The filename of the book image

```bash
curl -i -X GET http://localhost:5000/books/photos/filename.jpg
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 19:08:55 GMT
Content-Disposition: inline; filename=filename.jpg
Content-Type: image/jpeg
Content-Length: 218604
Last-Modified: Sun, 21 Jul 2024 19:05:48 GMT
Cache-Control: no-cache
ETag: "1721588748.296946-218604-1869223763"
Date: Sun, 21 Jul 2024 19:08:55 GMT
Connection: close

[Binary image data]
```

> Tip: Use this endpoint in your front end to display the image

### Possible errors

- [DatabaseConnection](./errors.md#databaseconnection)
- [ImageNotFound](./errors.md#imagenotfound)
- [MethodNotAllowed](./errors.md#methodnotallowed)

<br/>

## Add image to a book

Add an image to a book providing the book ID and a file.

### Request

`POST /books/<id_book>/photos`

#### URL parameters

- `id_book` (Number) - Book's ID

#### Content-Type

- `multipart/form-data`

#### Payload fields

- `img` (File) - Book image's file
  - Accepted files: `png`, `jpg` and `jpeg`
  - Max size: `7MB`

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X POST \
-H "Content-Type: multipart/form-data" \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
-F "img=@/path/to/your/image.jpg" \
http://localhost:5000/books/1/photos
```

### Response `201 CREATED`

```http
HTTP/1.1 201 CREATED
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 19:28:11 GMT
Content-Type: application/json
Content-Length: 93
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "id": 1,
    "img_url": "http://localhost:5000/books/photos/filename.jpg"
}
```

#### Response fields

- `img_url` (String) - Book image's URL (file converted to `jpg`)
- `id` (Number) - Book image's ID

### Possible errors

- [BookAlreadyHaveImageMaxQty](./errors.md#bookgenrealreadyexists)
- [BookDoesntExist](./errors.md#bookdoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidContentType](./errors.md#invalidcontenttype)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidDataSent](./errors.md#invaliddatasent)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)
- [NoDataSent](./errors.md#nodatasent)

<br/>

## Update book image

Update a book image based on its book ID and image ID providing a file.

### Request

`PATCH /books/<id_book>/photos/<id_img>`

#### URL parameters

- `id_book` (Number) - Book's ID
- `id_img` (Number) - Book image's ID

#### Content-Type

- `multipart/form-data`

#### Payload fields

- `img` (File) - Book image's file
  - Accepted files: `png`, `jpg` and `jpeg`
  - Max size: `7MB`

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X PATCH \
-H "Content-Type: multipart/form-data" \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
-F "img=@/path/to/your/image.jpg" \
http://localhost:5000/books/1/photos/1
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 19:55:33 GMT
Content-Type: application/json
Content-Length: 93
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "id": 1,
    "img_url": "http://localhost:5000/books/photos/filename.jpg"
}
```

#### Response fields

- `img_url` (String) - Book image's URL (file converted to `jpg`)
- `id` (Number) - Book image's ID

### Possible errors

- [BookImgDoesntExist](./errors.md#bookimgdoesntexist)
- [BookDoesntExist](./errors.md#bookdoesntexist)
- [BookDoesntOwnThisImg](./errors.md#bookdoesntownthisimg)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidContentType](./errors.md#invalidcontenttype)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidDataSent](./errors.md#invaliddatasent)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)
- [NoDataSent](./errors.md#nodatasent)

<br/>

## Delete book image

Delete a book image based on its book ID and image ID.

### Request

`DELETE /books/<id_book>/photos/<id_img>`

#### URL parameters

- `id_book` (Number) - Book's ID
- `id_img` (Number) - Book image's ID

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X DELETE \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
http://localhost:5000/books/1/photos/1
```

### Response `204 NO CONTENT`

```http
HTTP/1.1 204 NO CONTENT
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 19:20:43 GMT
Content-Type: application/json
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close
```

### Possible errors

- [BookImgDoesntExist](./errors.md#bookimgdoesntexist)
- [BookDoesntExist](./errors.md#bookdoesntexist)
- [BookDoesntOwnThisImg](./errors.md#bookdoesntownthisimg)
- [BookMustHaveAtLeastOneImg](./errors.md#bookmusthaveatleastoneimg)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)

<br/>

# Book keywords

## Create book keyword

Add a keyword to a book providing the book ID.

### Request

`POST /books/<id_book>/keywords`

#### URL parameters

- `id_book` (Number) - Book's ID

#### Content-Type

- `application/json`

#### Payload fields

- `keyword` (String) - Book keyword
  - Min size: `3`
  - Max size: `20`
  - Pattern: `^[a-zA-ZÀ-ÿç\s\d]+$` (Allows letters, numbers, spaces, and accented characters)

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X POST \
-H "Content-Type: application/json" \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
-d '{
    "keyword": "String"
}' \
http://localhost:5000/books/1/keywords
```

### Response `201 CREATED`

```http
HTTP/1.1 201 CREATED
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 23:53:55 GMT
Content-Type: application/json
Content-Length: 29
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "id": 1,
    "keyword": "string"
}
```

#### Response fields

- `keyword` (String) - Book keyword's name (converted to lowercase and whitespace stripped)
- `id` (Number) - Book keyword's ID

### Possible errors

- [BookDoesntExist](./errors.md#bookdoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidContentType](./errors.md#invalidcontenttype)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidDataSent](./errors.md#invaliddatasent)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)
- [NoDataSent](./errors.md#nodatasent)

<br/>

## Delete book keyword

Delete a book keyword based on its book ID and keyword ID.

### Request

`DELETE /books/<id_book>/keywords/<id_keyword>`

#### URL parameters

- `id_book` (Number) - Book's ID
- `id_keyword` (Number) - Book keyword's ID

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X DELETE \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
http://localhost:5000/books/1/keywords/1
```

### Response `204 NO CONTENT`

```http
HTTP/1.1 204 NO CONTENT
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 23:58:28 GMT
Content-Type: application/json
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close
```

### Possible errors

- [BookDoesntExist](./errors.md#bookdoesntexist)
- [BookDoesntOwnThisKeyword](./errors.md#bookdoesntownthiskeyword)
- [BookMustHaveAtLeastOneKeyword](./errors.md#bookmusthaveatleastonekeyword)
- [BookKeywordDoesntExist](./errors.md#bookkeyworddoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)

<br/>

# Book kinds

## Get all book kinds

Get a pagination with all book kinds.

### Request

`GET /bookKinds?page=<page>`

#### URL parameters

- (Optional) `page` (Number) - Page's number (if not provided, it'll be `1`)

```bash
curl -i -X GET http://localhost:5000/bookKinds?page=1
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 16:39:26 GMT
Content-Length: 186
Content-Type: application/json
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "data":[
        {
            "kind": "string",
            "id": 1
        }
    ],
    "has_next": false,
    "has_prev": false,
    "next_page": null,
    "page": 1,
    "per_page": 20,
    "prev_page": null,
    "total_items": 1,
    "total_pages": 1
}
```

#### Response fields

- `data` (Array) - Array with all book kinds
  - `kind` (String) - Book kind's name
  - `id` (Number) - Book kind's ID
- `has_next` (Boolean) - Whether there's a next page
- `has_prev` (Boolean) - Whether there's a previous page
- `next_page` (Null | String) - Next page's URL if it exists (e.g. /bookKinds?page=2)
- `page` (Number) - Current page
- `per_page` (Number) - Total items for each page
- `prev_page` (Null | String) - Previous page's URL if it exists (e.g. /bookKinds?page=1)
- `total_items` (Number) - Total items returned
- `total_pages` (Number) - Total page quantity

### Possible errors

- [DatabaseConnection](./errors.md#databaseconnection)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [PaginationPageDoesntExist](./errors.md#paginationpagedoesntexist)

<br/>

## Get book kind by ID

Get a book kind by its ID.

### Request

`GET /bookKinds/<id>`

#### URL parameters

- `id` (Number) - Book kind's ID

```bash
curl -i -X GET http://localhost:5000/bookKinds/1
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 17:25:11 GMT
Content-Type: application/json
Content-Length: 52
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "kind": "string",
    "id": 1
}
```

#### Response fields

- `kind` (String) - Book kind's name
- `id` (Number) - Book kind's ID

### Possible errors

- [BookKindDoesntExist](./errors.md#bookkinddoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [MethodNotAllowed](./errors.md#methodnotallowed)

<br/>

## Create book kind

Create a book kind providing its name.

### Request

`POST /bookKinds`

#### Content-Type

- `application/json`

#### Payload fields

- `kind` (String) - Book kind's name
  - Min length: `3`
  - Max length: `30`
  - Pattern: `^[a-zA-ZÀ-ÿç\s]+$` (Allows letters, spaces, and accented characters)

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X POST \
-H "Content-Type: application/json" \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
-d '{
    "kind": "String"
}' \
http://localhost:5000/bookKinds
```

### Response `201 CREATED`

```http
HTTP/1.1 201 CREATED
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 17:45:29 GMT
Content-Type: application/json
Content-Length: 26
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "kind": "string",
    "id": 1
}
```

#### Response fields

- `kind` (String) - Book kind's name (converted to lowercase and whitespace stripped)
- `id` (Number) - Book kind's ID

### Possible errors

- [BookKindAlreadyExists](./errors.md#bookkindalreadyexists)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidContentType](./errors.md#invalidcontenttype)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidDataSent](./errors.md#invaliddatasent)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)
- [NoDataSent](./errors.md#nodatasent)

<br/>

## Update book kind

Update a book kind by its ID providing its name.

### Request

`PATCH /bookKinds/<id>`

#### URL parameters

- `id` (Number) - Book kind's ID

#### Content-Type

- `application/json`

#### Payload fields

- `kind` (String) - Book kind's name
  - Min length: `3`
  - Max length: `30`
  - Pattern: `^[a-zA-ZÀ-ÿç\s]+$` (Allows letters, spaces, and accented characters)

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X PATCH \
-H "Content-Type: application/json" \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
-d '{
    "kind": "String"
}' \
http://localhost:5000/bookKinds/1
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 18:00:21 GMT
Content-Type: application/json
Content-Length: 29
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "kind": "string",
    "id": 1
}
```

#### Response fields

- `kind` (String) - Book kind's name (converted to lowercase and whitespace stripped)
- `id` (Number) - Book kind's ID

### Possible errors

- [BookKindAlreadyExists](./errors.md#bookkindalreadyexists)
- [BookKindDoesntExist](./errors.md#bookkinddoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidContentType](./errors.md#invalidcontenttype)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidDataSent](./errors.md#invaliddatasent)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)
- [NoDataSent](./errors.md#nodatasent)

<br/>

## Delete book kind

Delete a book kind by its ID.

### Request

`DELETE /bookKinds/<id>`

#### URL parameters

- `id` (Number) - Book kind's ID

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X DELETE \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
http://localhost:5000/bookKinds/1
```

### Response `204 NO CONTENT`

```http
HTTP/1.1 204 NO CONTENT
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 18:42:55 GMT
Content-Type: application/json
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close
```

### Possible errors

- [BookKindDoesntExist](./errors.md#bookkinddoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)
- [ThereAreLinkedBooksWithThisBookKind](./errors.md#therearelinkedbookswiththisbookkind)

<br/>

# Books

## Get all books

Get a pagination with all books.

### Request

`GET /books?page=<page>`

#### URL parameters

- (Optional) `page` (Number) - Page's number (if not provided, it'll be `1`)

```bash
curl -i -X GET http://localhost:5000/books?page=1
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Mon, 22 Jul 2024 13:53:03 GMT
Content-Type: application/json
Content-Length: 588
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "data": [
        {
            "author": "String",
            "book_genre": {
                "genre": "string",
                "id": 1
            },
            "book_imgs": [
                {
                    "id": 1,
                    "img_url": "http://localhost:5000/books/photos/filename.jpg"
                }
            ],
            "book_keywords": [
                {
                    "id": 1,
                    "keyword": "string"
                }
            ],
            "book_kind": {
                "id": 1,
                "kind": "string"
            },
            "id": 1,
            "name": "String",
            "price": 100.0,
            "release_year": 2000
        }
    ],
    "has_next": false,
    "has_prev": false,
    "next_page": null,
    "page": 1,
    "per_page": 20,
    "prev_page": null,
    "total_items": 1,
    "total_pages": 1
}
```

#### Response fields

- `data` (Array) - Array with all books
  - `author` (String) - Book's author
  - `book_genre` (Object) - Book's genre
    - `genre` (String) - Book genre's name
    - `id` (Number) - Book genre's ID
  - `book_imgs` (Array) - Array with all book's images
    - `id` (Number) - Book image's ID
    - `img_url` (String) - Book image's URL
  - `book_keywords` (Array) - Array with all book's keywords
    - `id` (Number) - Book keyword's ID
    - `keyword` (String) - Book keyword's name
  - `book_kind` (Object) - Book's kind
    - `id` (Number) - Book kind's ID
    - `kind` (String) - Book kind's name
  - `id` (Number) - Book's ID
  - `name` (String) - Book's name
  - `price` (Number) - Book's price (as float)
  - `release_year` (Number) - Book's release year
- `has_next` (Boolean) - Whether there's a next page
- `has_prev` (Boolean) - Whether there's a previous page
- `next_page` (Null | String) - Next page's URL if it exists (e.g. /books?page=2)
- `page` (Number) - Current page
- `per_page` (Number) - Total items for each page
- `prev_page` (Null | String) - Previous page's URL if it exists (e.g. /books?page=1)
- `total_items` (Number) - Total items returned
- `total_pages` (Number) - Total page quantity

### Possible errors

- [DatabaseConnection](./errors.md#databaseconnection)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [PaginationPageDoesntExist](./errors.md#paginationpagedoesntexist)

<br/>

## Get book by ID

Get a book by its ID.

### Request

`GET /books/<id>`

#### URL parameters

- `id` (Number) - Book's ID

```bash
curl -i -X GET http://localhost:5000/books/1
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Mon, 22 Jul 2024 15:11:32 GMT
Content-Type: application/json
Content-Length: 454
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "author": "String",
    "book_genre": {
        "genre": "string",
        "id": 1
    },
    "book_imgs": [
        {
            "id": 1,
            "img_url": "http://localhost:5000/books/photos/filename.jpg"
        }
    ],
    "book_keywords": [
        {
            "id": 1,
            "keyword": "string"
        }
    ],
    "book_kind": {
        "id": 1,
        "kind": "string"
    },
    "id": 1,
    "name": "String",
    "price": 100.0,
    "release_year": 2000
}
```

#### Response fields

- `author` (String) - Book's author
- `book_genre` (Object) - Book's genre
  - `genre` (String) - Book genre's name
  - `id` (Number) - Book genre's ID
- `book_imgs` (Array) - Array with all book's images
  - `id` (Number) - Book image's ID
  - `img_url` (String) - Book image's URL
- `book_keywords` (Array) - Array with all book's keywords
  - `id` (Number) - Book keyword's ID
  - `keyword` (String) - Book keyword's name
- `book_kind` (Object) - Book's kind
  - `id` (Number) - Book kind's ID
  - `kind` (String) - Book kind's name
- `id` (Number) - Book's ID
- `name` (String) - Book's name
- `price` (Number) - Book's price (as float)
- `release_year` (Number) - Book's release year

### Possible errors

- [BookDoesntExist](./errors.md#bookdoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [MethodNotAllowed](./errors.md#methodnotallowed)

<br/>

## Create book

Create a book.

### Request

`POST /books`

#### Content-Type

- `multipart/form-data`

#### Payload fields

- `name` (String) - Book's name
  - Min length: `2`
  - Max length: `80`
  - Pattern: `^[a-zA-ZÀ-ÿç\s\d-]+$` (Allows letters, numbers, spaces, and accented characters)
- `price` (Number) - Book's price
  - format: `Integer` or `Float`
  - Greater than: `0`
  - Max digits: `6`
  - Max decimal places: `2`
- `author` (String) - Book's author
  - Min length: `3`
  - Max length: `40`
  - Pattern: `^[a-zA-ZÀ-ÿç\s]+$` (Allows letters, spaces, and accented characters)
- `release_year` (Number) - Book's release year
  - format: `Integer`
  - Greater than: `1000`
  - Less than: `datetime.now().year`
- `keywords` (String) - Book's keywords
  - format: `keyword 1[;keyword 2[;keyword 3...]]`
- `id_book_kind` (Number) - Book kind's ID
  - format: `Integer`
  - Greater than: `0`
- `id_book_genre` (Number) - Book genre's ID
  - format: `Integer`
  - Greater than: `0`
- `imgs` (Mutiple files) - Book's images
  - Min quantity: `1`
  - Max quantity: `5`
  - Accepted files: `png`, `jpg` and `jpeg`
  - Max size for each file: `7MB`

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X POST \
-H "Content-Type: multipart/form-data" \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
-F "name=String" \
-F "price=100" \
-F "author=String" \
-F "release_year=2000" \
-F 'keywords="kw 1;kw 2"' \
-F "id_book_kind=1" \
-F "id_book_genre=1" \
-F "imgs=@/path/to/images/image 1.png" \
-F "imgs=@/path/to/images/image 2.jpeg" \
http://localhost:5000/books
```

### Response `201 CREATED`

```http
HTTP/1.1 201 CREATED
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Mon, 22 Jul 2024 16:20:32 GMT
Content-Type: application/json
Content-Length: 467
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "author": "String",
    "book_genre": {
        "genre": "string",
        "id": 1
    },
    "book_imgs": [
        {
            "id": 1,
            "img_url": "http://localhost:5000/books/photos/filename.jpg"
        }
    ],
    "book_keywords": [
        {
            "id": 1,
            "keyword": "string"
        }
    ],
    "book_kind": {
        "id": 1,
        "kind": "string"
    },
    "id": 1,
    "name": "String",
    "price": 100.0,
    "release_year": 2000
}
```

#### Response fields

- `author` (String) - Book's author (whitespace stripped)
- `book_genre` (Object) - Book's genre
  - `genre` (String) - Book genre's name
  - `id` (Number) - Book genre's ID
- `book_imgs` (Array) - Array with all book's images
  - `id` (Number) - Book image's ID
  - `img_url` (String) - Book image's URL (file converted to jpg)
- `book_keywords` (Array) - Array with all book's keywords
  - `id` (Number) - Book keyword's ID
  - `keyword` (String) - Book keyword's name (converted to lowercase and whitespace stripped)
- `book_kind` (Object) - Book's kind
  - `id` (Number) - Book kind's ID
  - `kind` (String) - Book kind's name
- `id` (Number) - Book's ID
- `name` (String) - Book's name (whitespace stripped)
- `price` (Number) - Book's price (as float)
- `release_year` (Number) - Book's release year

### Possible errors

- [BookAlreadyExists](./errors.md#bookalreadyexists)
- [BookGenreDoesntExist](./errors.md#bookgenredoesntexist)
- [BookKindDoesntExist](./errors.md#bookkinddoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidContentType](./errors.md#invalidcontenttype)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidDataSent](./errors.md#invaliddatasent)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)
- [NoDataSent](./errors.md#nodatasent)

<br/>

## Update book

Update a book by its ID.

### Request

`PATCH /books/<id>`

#### URL parameters

- `id` (Number) - Book's ID

#### Content-Type

- `multipart/form-data`

#### Payload fields

- (Optional) `name` (String) - Book's name
  - Min length: `2`
  - Max length: `80`
  - Pattern: `^[a-zA-ZÀ-ÿç\s\d-]+$` (Allows letters, numbers, spaces, and accented characters)
- (Optional) `price` (Number) - Book's price
  - format: `Integer` or `Float`
  - Greater than: `0`
  - Max digits: `6`
  - Max decimal places: `2`
- (Optional) `author` (String) - Book's author
  - Min length: `3`
  - Max length: `40`
  - Pattern: `^[a-zA-ZÀ-ÿç\s]+$` (Allows letters, spaces, and accented characters)
- (Optional) `release_year` (Number) - Book's release year
  - format: `Integer`
  - Greater than: `1000`
  - Less than: `datetime.now().year`
- (Optional) `id_book_kind` (Number) - Book kind's ID
  - format: `Integer`
  - Greater than: `0`
- (Optional) `id_book_genre` (Number) - Book genre's ID
  - format: `Integer`
  - Greater than: `0`

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X PATCH \
-H "Content-Type: multipart/form-data" \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
-F "name=String" \
-F "price=100" \
-F "author=String" \
-F "release_year=2000" \
-F "id_book_kind=1" \
-F "id_book_genre=1" \
http://localhost:5000/books/1
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Mon, 22 Jul 2024 20:02:14 GMT
Content-Type: application/json
Content-Length: 552
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "author": "String",
    "book_genre": {
        "genre": "string",
        "id": 1
    },
    "book_imgs": [
        {
            "id": 1,
            "img_url": "http://localhost:5000/books/photos/filename.jpg"
        }
    ],
    "book_keywords": [
        {
            "id": 1,
            "keyword": "string"
        }
    ],
    "book_kind": {
        "id": 1,
        "kind": "string"
    },
    "id": 1,
    "name": "String",
    "price": 100.0,
    "release_year": 2000
}
```

#### Response fields

- `author` (String) - Book's author (whitespace stripped)
- `book_genre` (Object) - Book's genre
  - `genre` (String) - Book genre's name
  - `id` (Number) - Book genre's ID
- `book_imgs` (Array) - Array with all book's images
  - `id` (Number) - Book image's ID
  - `img_url` (String) - Book image's URL
- `book_keywords` (Array) - Array with all book's keywords
  - `id` (Number) - Book keyword's ID
  - `keyword` (String) - Book keyword's name
- `book_kind` (Object) - Book's kind
  - `id` (Number) - Book kind's ID
  - `kind` (String) - Book kind's name
- `id` (Number) - Book's ID
- `name` (String) - Book's name (whitespace stripped)
- `price` (Number) - Book's price (as float)
- `release_year` (Number) - Book's release year

> To manage book images see [Book image's section](#book-images), and to manage book keywords see [Book keyword's section](#book-keywords).

### Possible errors

- [BookAlreadyExists](./errors.md#bookalreadyexists)
- [BookGenreDoesntExist](./errors.md#bookgenredoesntexist)
- [BookKindDoesntExist](./errors.md#bookkinddoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidContentType](./errors.md#invalidcontenttype)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidDataSent](./errors.md#invaliddatasent)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)
- [NoDataSent](./errors.md#nodatasent)

<br/>

## Delete book

Delete a book as well its keywords and images by its ID.

### Request

`DELETE /books/<id>`

#### URL parameters

- `id` (Number) - Book's ID

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X DELETE \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
http://localhost:5000/books/1
```

### Response `204 NO CONTENT`

```http
HTTP/1.1 204 NO CONTENT
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Sun, 21 Jul 2024 18:42:55 GMT
Content-Type: application/json
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close
```

### Possible errors

- [BookDoesntExist](./errors.md#bookdoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)

<br/>

# Saved books

## Save a book

Save a book in your account.

### Request

`POST /books/<id>/save`

#### URL parameters

- `id` (Number) - Book's ID

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X POST \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
http://localhost:5000/books/1/save
```

### Response `201 CREATED`

```http
HTTP/1.1 201 CREATED
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Mon, 22 Jul 2024 20:28:32 GMT
Content-Type: application/json
Content-Length: 552
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "author": "String",
    "book_genre": {
        "genre": "string",
        "id": 1
    },
    "book_imgs": [
        {
            "id": 1,
            "img_url": "http://localhost:5000/books/photos/filename.jpg"
        }
    ],
    "book_keywords": [
        {
            "id": 1,
            "keyword": "string"
        }
    ],
    "book_kind": {
        "id": 1,
        "kind": "string"
    },
    "id": 1,
    "name": "String",
    "price": 100.0,
    "release_year": 2000
}
```

#### Response fields

- `author` (String) - Book's author (whitespace stripped)
- `book_genre` (Object) - Book's genre
  - `genre` (String) - Book genre's name
  - `id` (Number) - Book genre's ID
- `book_imgs` (Array) - Array with all book's images
  - `id` (Number) - Book image's ID
  - `img_url` (String) - Book image's URL (file converted to jpg)
- `book_keywords` (Array) - Array with all book's keywords
  - `id` (Number) - Book keyword's ID
  - `keyword` (String) - Book keyword's name (converted to lowercase and whitespace stripped)
- `book_kind` (Object) - Book's kind
  - `id` (Number) - Book kind's ID
  - `kind` (String) - Book kind's name
- `id` (Number) - Book's ID
- `name` (String) - Book's name (whitespace stripped)
- `price` (Number) - Book's price (as float)
- `release_year` (Number) - Book's release year

### Possible errors

- [BookAlreadySaved](./errors.md#bookalreadysaved)
- [BookDoesntExist](./errors.md#bookdoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)

<br/>

## Get all saved books

Get a pagination with all user saved books.

### Request

`GET /books/saved?page=<page>`

#### URL parameters

- (Optional) `page` (Number) - Page's number (if not provided, it'll be `1`)

#### Headers and cookies

- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X GET \
-b "access_token_cookie=your_access_token" \
http://localhost:5000/books/saved
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Mon, 22 Jul 2024 13:53:03 GMT
Content-Type: application/json
Content-Length: 588
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "data": [
        {
            "author": "String",
            "book_genre": {
                "genre": "string",
                "id": 1
            },
            "book_imgs": [
                {
                    "id": 1,
                    "img_url": "http://localhost:5000/books/photos/filename.jpg"
                }
            ],
            "book_keywords": [
                {
                    "id": 1,
                    "keyword": "string"
                }
            ],
            "book_kind": {
                "id": 1,
                "kind": "string"
            },
            "id": 1,
            "name": "String",
            "price": 100.0,
            "release_year": 2000
        }
    ],
    "has_next": false,
    "has_prev": false,
    "next_page": null,
    "page": 1,
    "per_page": 20,
    "prev_page": null,
    "total_items": 1,
    "total_pages": 1
}
```

#### Response fields

- `data` (Array) - Array with all saved books
  - `author` (String) - Book's author
  - `book_genre` (Object) - Book's genre
    - `genre` (String) - Book genre's name
    - `id` (Number) - Book genre's ID
  - `book_imgs` (Array) - Array with all book's images
    - `id` (Number) - Book image's ID
    - `img_url` (String) - Book image's URL
  - `book_keywords` (Array) - Array with all book's keywords
    - `id` (Number) - Book keyword's ID
    - `keyword` (String) - Book keyword's name
  - `book_kind` (Object) - Book's kind
    - `id` (Number) - Book kind's ID
    - `kind` (String) - Book kind's name
  - `id` (Number) - Book's ID
  - `name` (String) - Book's name
  - `price` (Number) - Book's price (as float)
  - `release_year` (Number) - Book's release year
- `has_next` (Boolean) - Whether there's a next page
- `has_prev` (Boolean) - Whether there's a previous page
- `next_page` (Null | String) - Next page's URL if it exists (e.g. /books/saved?page=2)
- `page` (Number) - Current page
- `per_page` (Number) - Total items for each page
- `prev_page` (Null | String) - Previous page's URL if it exists (e.g. /books/saved?page=1)
- `total_items` (Number) - Total items returned
- `total_pages` (Number) - Total page quantity

### Possible errors

- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingJWT](./errors.md#missingjwt)
- [PaginationPageDoesntExist](./errors.md#paginationpagedoesntexist)

<br/>

## Delete saved book

Delete a saved book from your account.

### Request

`DELETE /books/saved/<id>`

#### URL parameters

- `id` (Number) - Book's ID

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X DELETE \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
http://localhost:5000/books/saved/1
```

### Response `204 NO CONTENT`

```http
HTTP/1.1 204 NO CONTENT
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Mon, 22 Jul 2024 20:44:44 GMT
Content-Type: application/json
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close
```

### Possible errors

- [BookDoesntExist](./errors.md#bookdoesntexist)
- [BookIsNotSaved](./errors.md#bookisnotsaved)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)

<br/>

# Search

## Search books

Get a pagination with all searched books.

### Request

`GET /search?page=<page>`

#### URL parameters

- (Optional) `page` (Number) - Page's number (if not provided, it'll be `1`)

#### Content-Type

- `application/json`

#### Payload fields

- (Optional) `query` (String) - Search's query (book's name, author or keyword)
- (Optional) `id_book_kind` (Number) - Book kind's ID
  - format: `Integer`
  - Greater than: `0`
- (Optional) `id_book_genre` (Number) - Book genre's ID
  - format: `Integer`
  - Greater than: `0`
- (Optional) `release_year` (Number) - Book's release year
  - format: `Integer`
  - Greater than: `0`
- (Optional) `min_price` (Number) - Book's min price
  - format: `Integer` or `Float`
  - Greater than: `0`
  - Max digits: `6`
  - Max decimal places: `2`
- (Optional) `max_price` (Number) - Book's max price
  - format: `Integer` or `Float`
  - Greater than: `0`
  - Max digits: `6`
  - Max decimal places: `2`

```bash
curl -i -X GET \
-H "Content-Type: application/json" \
-d '{
    "query": "String",
    "id_book_kind": 1,
    "id_book_genre": 1,
    "release_year": 2000,
    "min_price": 10.0,
    "max_price": 100.42
}' \
http://localhost:5000/search?page=1
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Mon, 22 Jul 2024 13:53:03 GMT
Content-Type: application/json
Content-Length: 588
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "data": [
        {
            "author": "String",
            "book_genre": {
                "genre": "string",
                "id": 1
            },
            "book_imgs": [
                {
                    "id": 1,
                    "img_url": "http://localhost:5000/books/photos/filename.jpg"
                }
            ],
            "book_keywords": [
                {
                    "id": 1,
                    "keyword": "string"
                }
            ],
            "book_kind": {
                "id": 1,
                "kind": "string"
            },
            "id": 1,
            "name": "String",
            "price": 100.0,
            "release_year": 2000
        }
    ],
    "has_next": false,
    "has_prev": false,
    "next_page": null,
    "page": 1,
    "per_page": 20,
    "prev_page": null,
    "total_items": 1,
    "total_pages": 1
}
```

#### Response fields

- `data` (Array) - Array with all searched books
  - `author` (String) - Book's author
  - `book_genre` (Object) - Book's genre
    - `genre` (String) - Book genre's name
    - `id` (Number) - Book genre's ID
  - `book_imgs` (Array) - Array with all book's images
    - `id` (Number) - Book image's ID
    - `img_url` (String) - Book image's URL
  - `book_keywords` (Array) - Array with all book's keywords
    - `id` (Number) - Book keyword's ID
    - `keyword` (String) - Book keyword's name
  - `book_kind` (Object) - Book's kind
    - `id` (Number) - Book kind's ID
    - `kind` (String) - Book kind's name
  - `id` (Number) - Book's ID
  - `name` (String) - Book's name
  - `price` (Number) - Book's price (as float)
  - `release_year` (Number) - Book's release year
- `has_next` (Boolean) - Whether there's a next page
- `has_prev` (Boolean) - Whether there's a previous page
- `next_page` (Null | String) - Next page's URL if it exists (e.g. /books?page=2)
- `page` (Number) - Current page
- `per_page` (Number) - Total items for each page
- `prev_page` (Null | String) - Previous page's URL if it exists (e.g. /books?page=1)
- `total_items` (Number) - Total items returned
- `total_pages` (Number) - Total page quantity

### Possible errors

- [BookGenreDoesntExist](./errors.md#bookgenredoesntexist)
- [BookKindDoesntExist](./errors.md#bookkinddoesntexist)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidContentType](./errors.md#invalidcontenttype)
- [InvalidDataSent](./errors.md#invaliddatasent)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [NoDataSent](./errors.md#nodatasent)

<br/>

# Users

## Get user information

Get your authenticated user information.

### Request

`GET /users`

#### Headers and cookies

- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X GET \
-b "access_token_cookie=your_access_token" \
http://localhost:5000/users
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Tue, 23 Jul 2024 01:22:40 GMT
Content-Type: application/json
Content-Length: 115
Content-Type: application/json;charset=utf-8
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "id": 1,
    "img_url": "http://localhost:5000/users/photos/filename.jpg",
    "username": "String"
}
```
#### Response fields

- `id` (Number) - User's ID
- `img_url` (String) - User's image URL
- `username` (String) - User's username

### Possible errors

- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingJWT](./errors.md#missingjwt)

<br/>

## Get user image by filename

Retrieve the binary data of user image based on its filename.

### Request

`GET /users/photos/<filename>`

#### URL parameters

- `filename` (String) - The filename of the user image

```bash
curl -i -X GET http://localhost:5000/users/photos/filename.jpg
```

### Response `200 OK`

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Tue, 23 Jul 2024 14:57:01 GMT
Content-Disposition: inline; filename=filename.jpg
Content-Type: image/jpeg
Content-Length: 191160
Last-Modified: Tue, 23 Jul 2024 14:51:48 GMT
Cache-Control: no-cache
ETag: "1721746308.5349705-191160-1628903081"
Date: Tue, 23 Jul 2024 14:57:01 GMT
Connection: close

[Binary image data]
```

> Tip: Use this endpoint in your front end to display the image

### Possible errors

- [DatabaseConnection](./errors.md#databaseconnection)
- [ImageNotFound](./errors.md#imagenotfound)
- [MethodNotAllowed](./errors.md#methodnotallowed)

<br/>

## Create user

Create a user.

### Request

`POST /users`

#### Content-Type

- `multipart/form-data`

#### Payload fields

- `username` (String) - User's username
  - Min length: `4`
  - Max length: `50`
  - Pattern: `^[a-zA-Z\d_-]+$` (Allows letters, numbers, underscores and hypens)
- `password` (Number) - User's password
  - Necessary chars: A `lowercase` char, a `uppercase` char, a `special` char (!@#$%&*()_+=-,.:;?/\|) and a `number`
  - Min length: `8`
  - Max length: `255`
- `img` (Files) - User's image
  - Accepted files: `png`, `jpg` and `jpeg`
  - Max size for each file: `5MB`

```bash
curl -i -X POST \
-H "Content-Type: multipart/form-data" \
-F "username=String" \
-F "password=String_1" \
-F "img=@/path/to/image/image.jpg" \
http://localhost:5000/users
```

### Response `201 CREATED`

```http
HTTP/1.1 201 CREATED
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Tue, 23 Jul 2024 01:59:16 GMT
Content-Type: application/json
Content-Length: 122
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "id": 1,
    "img_url": "http://localhost:5000/users/photos/filename.jpg",
    "username": "String"
}
```
#### Response fields

- `id` (Number) - User's ID
- `img_url` (String) - User's image URL
- `username` (String) - User's username

### Possible errors

- [UserAlreadyAuthenticated](./errors.md#useralreadyauthenticated)
- [UserAlreadyExists](./errors.md#useralreadyexists)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidContentType](./errors.md#invalidcontenttype)
- [InvalidDataSent](./errors.md#invaliddatasent)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [NoDataSent](./errors.md#nodatasent)

<br/>

## Update user

Update your authenticated user.

### Request

`PATCH /users`

#### Content-Type

- `multipart/form-data`

#### Payload fields

- (Optional) `username` (String) - User's username
  - Min length: `4`
  - Max length: `50`
  - Pattern: `^[a-zA-Z\d_-]+$` (Allows letters, numbers, underscores and hypens)
- (Optional) `password` (Number) - User's password
  - Necessary chars: A `lowercase` char, a `uppercase` char, a `special` char (!@#$%&*()_+=-,.:;?/\|) and a `number`
  - Min length: `8`
  - Max length: `255`
- (Optional) `img` (Files) - User's image
  - Accepted files: `png`, `jpg` and `jpeg`
  - Max size for each file: `5MB`

```bash
curl -i -X PATCH \
-H "Content-Type: multipart/form-data" \
-F "username=String" \
-F "password=String_1" \
-F "img=@/path/to/image/image.jpg" \
http://localhost:5000/users
```

### Response `201 CREATED`

```http
HTTP/1.1 201 CREATED
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Tue, 23 Jul 2024 01:59:16 GMT
Content-Type: application/json
Content-Length: 122
Access-Control-Allow-Origin: http://127.0.0.1:5500
Access-Control-Allow-Headers: Content-Type,Authorization,X-CSRF-TOKEN
Access-Control-Allow-Credentials: true
Connection: close

{
    "id": 1,
    "img_url": "http://localhost:5000/users/photos/filename.jpg",
    "username": "String"
}
```
#### Response fields

- `id` (Number) - User's ID
- `img_url` (String) - User's image URL
- `username` (String) - User's username

### Possible errors

- [UserAlreadyExists](./errors.md#useralreadyexists)
- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidContentType](./errors.md#invalidcontenttype)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidDataSent](./errors.md#invaliddatasent)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)
- [NoDataSent](./errors.md#nodatasent)

<br/>

## Delete user

Delete the authenticated user along with their saved books and image, and redirect to the [Logout endpoint](#logout).

### Request

`DELETE /users`

#### Headers and cookies

- (header) `X-CSRF-TOKEN` - Header with your CSRF token
- (cookie) `access_token_cookie` - Your JWT cookie

```bash
curl -i -X DELETE \
-H "X-CSRF-TOKEN: your_csrf_token" \
-b "access_token_cookie=your_access_token" \
http://localhost:5000/users
```

### Response `302 FOUND`

```http
HTTP/1.1 302 FOUND
Server: Werkzeug/3.0.3 Python/3.10.14
Date: Tue, 23 Jul 2024 15:09:36 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 211
Location: /auth/logout
Connection: close
```

### Possible errors

- [DatabaseConnection](./errors.md#databaseconnection)
- [InvalidCSRF](./errors.md#invalidcsrf)
- [InvalidJWT](./errors.md#invalidjwt)
- [MethodNotAllowed](./errors.md#methodnotallowed)
- [MissingCSRF](./errors.md#missingcsrf)
- [MissingJWT](./errors.md#missingjwt)
