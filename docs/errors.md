# Errors

The API errors can be in the following formats:

```json
{
    "code": "ErrorName",
    "scope": "ErrorScope",
    "message": "Error message",
    "status": 400,
    "timestamp": "YYYY-MM-DDTHH:MM:SS.ssssss+00:00"
}
```

or

```json
{
    "code": "ErrorName",
    "scope": "ErrorScope",
    "message": "Error message",
    "detail": [
        {
            "loc": ["payload_field"], // or ["payload_field", index]
            "msg": "Validation error message",
            "type": "error_type"
        },
    ],
    "status": 400,
    "timestamp": "YYYY-MM-DDTHH:MM:SS.ssssss+00:00"
}
```

Below you'll find all API errors, organized by scope.

<br/>

# Table of contents

- [GeneralException](#generalexception)
  - [DatabaseConnection](#databaseconnection)
  - [MethodNotAllowed](#methodnotallowed)
  - [InvalidContentType](#invalidcontenttype)
  - [NoDataSent](#nodatasent)
  - [InvalidDataSent](#invaliddatasent)
  - [EndpointNotFound](#endpointnotfound)
  - [PaginationPageDoesntExist](#paginationpagedoesntexist)
- [AuthException](#authexception)
  - [InvalidLogin](#invalidlogin)
  - [UserAlreadyAuthenticated](#useralreadyauthenticated)
- [BookException](#bookexception)
  - [BookAlreadyExists](#bookalreadyexists)
  - [BookDoesntExist](#bookdoesntexist)
- [BookGenreException](#bookgenreexception)
  - [BookGenreAlreadyExists](#bookgenrealreadyexists)
  - [BookGenreDoesntExist](#bookgenredoesntexist)
  - [ThereAreLinkedBooksWithThisBookGenre](#therearelinkedbookswiththisbookgenre)
- [BookImgException](#bookimgexception)
  - [BookImgDoesntExist](#bookimgdoesntexist)
  - [BookDoesntOwnThisImg](#bookdoesntownthisimg)
  - [BookMustHaveAtLeastOneImg](#bookmusthaveatleastoneimg)
  - [BookAlreadyHaveImageMaxQty](#bookalreadyhaveimagemaxqty)
- [BookKeywordException](#bookkeywordexception)
  - [BookKeywordDoesntExist](#bookkeyworddoesntexist)
  - [BookDoesntOwnThisKeyword](#bookdoesntownthiskeyword)
  - [BookMustHaveAtLeastOneKeyword](#bookmusthaveatleastonekeyword)
- [BookKindException](#bookkindexception)
  - [BookKindAlreadyExists](#bookkindalreadyexists)
  - [BookKindDoesntExist](#bookkinddoesntexist)
  - [ThereAreLinkedBooksWithThisBookKind](#therearelinkedbookswiththisbookkind)
- [ImageException](#imageexception)
  - [ImageNotFound](#imagenotfound)
- [SavedBookException](#savedbookexception)
  - [BookIsNotSaved](#bookisnotsaved)
  - [BookAlreadySaved](#bookalreadysaved)
- [SecurityException](#securityexception)
  - [InvalidJWT](#invalidjwt)
  - [MissingJWT](#missingjwt)
  - [MissingCSRF](#missingcsrf)
  - [InvalidCSRF](#invalidcsrf)
- [UserException](#userexception)
  - [UserAlreadyExists](#useralreadyexists)

<br/>

# GeneralException

## DatabaseConnection

Returned when the API can't connect to [Frigatto Books Database](https://github.com/Alberto-Frigatto/frigatto-books-database) during a request.

### Status

`500 Internal Server Error`

### Message

`Unable to connect to the database`

### Example

```json
{
    "code": "DatabaseConnection",
    "scope": "GeneralException",
    "message": "Unable to connect to the database",
    "status": 500,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## MethodNotAllowed

Returned when you request an endpoint with HTTP method not allowed.

### Status

`405 Method Not Allowed`

### Message

`HTTP method not allowed`

### Example

```json
{
    "code": "MethodNotAllowed",
    "scope": "GeneralException",
    "message": "HTTP method not allowed",
    "status": 405,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## InvalidContentType

Returned when you request an endpoint with invalid/unexpected `Content-Type` header.

### Status

`415 Unsupported Media Type`

### Message

`Invalid Content-Type header`

### Example

```json
{
    "code": "InvalidContentType",
    "scope": "GeneralException",
    "message": "Invalid Content-Type header",
    "status": 415,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## NoDataSent

Returned when you request a must-payload endpoint without payload.

### Status

`400 Bad Request`

### Message

`No data sent`

### Example

```json
{
    "code": "NoDataSent",
    "scope": "GeneralException",
    "message": "No data sent",
    "status": 400,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## InvalidDataSent

Returned when you request an endpoint with an invalid payload.

### Status

`400 Bad Request`

### Detail

This error has error details about each payload field.

### Message

`Invalid data sent`

### Example

```json
{
    "code": "InvalidDataSent",
    "scope": "GeneralException",
    "message": "Invalid data sent",
    "detail":[
        {
            "loc":["username"],
            "msg":"String should match pattern '^[a-zA-Z\\d_-]+$'",
            "type":"string_pattern_mismatch"
        },
        {
            "loc":["password"],
            "msg":"Value error, The provided password has not the necessary chars",
            "type":"value_error"
        },
        {
            "loc":["img"],
            "msg":"Value error, The provided file is not an image",
            "type":"value_error"
        }
    ],
    "status": 400,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## EndpointNotFound

Returned when you request an endpoint that doesn't exist.

### Status

`404 Not Found`

### Message

`The endpoint does not exist`

### Example

```json
{
    "code": "EndpointNotFound",
    "scope": "GeneralException",
    "message": "The endpoint does not exist",
    "status": 404,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## PaginationPageDoesntExist

Returned when you request a pagination page that doesn't exist.

### Status

`404 Not Found`

### Message

`The page {page} does not exist`

### Example

```json
{
    "code": "PaginationPageDoesntExist",
    "scope": "GeneralException",
    "message": "The page 3 does not exist",
    "status": 404,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

# AuthException

## InvalidLogin

Returned when you provide invalid credentials to login.

### Status

`401 Unauthorized`

### Message

`Invalid username or password`

### Example

```json
{
    "code": "InvalidLogin",
    "scope": "AuthException",
    "message": "Invalid username or password",
    "status": 401,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## UserAlreadyAuthenticated

Returned when you're authenticated and try to login.

### Status

`400 Bad Request`

### Message

`The user is already logged in`

### Example

```json
{
    "code": "UserAlreadyAuthenticated",
    "scope": "AuthException",
    "message": "The user is already logged in",
    "status": 400,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

# BookException

## BookAlreadyExists

Returned when you try to create or update a book with name from a book already exists.

### Status

`409 Conflict`

### Message

`The book "{name}" already exists`

### Example

```json
{
    "code": "BookAlreadyExists",
    "scope": "BookException",
    "message": "The book \"The Godfather\" already exists",
    "status": 409,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## BookDoesntExist

Returned when you try to get, update, delete or save a book that doesn't exist.

### Status

`404 Not Found`

### Message

`The book {id} does not exist`

### Example

```json
{
    "code": "BookDoesntExist",
    "scope": "BookException",
    "message": "The book 4 does not exist",
    "status": 404,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

# BookGenreException

## BookGenreAlreadyExists

Returned when you try to create or update a book genre with name from a genre already exists.

### Status

`409 Conflict`

### Message

`The book genre "{name}" already exists`

### Example

```json
{
    "code": "BookGenreAlreadyExists",
    "scope": "BookGenreException",
    "message": "The book genre \"mistery\" already exists",
    "status": 409,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## BookGenreDoesntExist

Returned when you try to get, update or delete a book genre that doesn't exist.

### Status

`404 Not Found`

### Message

`The book genre {id} does not exist`

### Example

```json
{
    "code": "BookGenreDoesntExist",
    "scope": "BookGenreException",
    "message": "The book genre 4 does not exist",
    "status": 404,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## ThereAreLinkedBooksWithThisBookGenre

Returned when you try to delete a book genre referenced by at least 1 book.

### Status

`409 Conflict`

### Message

`The book genre {id} cannot be deleted because there are books linked to this genre`

### Example

```json
{
    "code": "ThereAreLinkedBooksWithThisBookGenre",
    "scope": "BookGenreException",
    "message": "The book genre 2 cannot be deleted because there are books linked to this genre",
    "status": 409,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

# BookImgException

## BookImgDoesntExist

Returned when you try to update or delete a book image that doesn't exist.

### Status

`404 Not Found`

### Message

`The image {id} does not exist`

### Example

```json
{
    "code": "BookImgDoesntExist",
    "scope": "BookImgException",
    "message": "The image 12 does not exist",
    "status": 404,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## BookDoesntOwnThisImg

Returned when you try to update or delete a book image from a book doesn't own it.

### Status

`403 Forbidden`

### Message

`The image {id_img} does not belong to the book {id_book}`

### Example

```json
{
    "code": "BookDoesntOwnThisImg",
    "scope": "BookImgException",
    "message": "The image 46 does not belong to the book 7",
    "status": 403,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## BookMustHaveAtLeastOneImg

Returned when you try to delete the last image from a book.

### Status

`400 Bad Request`

### Message

`The book {id_book} must have at least one image`

### Example

```json
{
    "code": "BookMustHaveAtLeastOneImg",
    "scope": "BookImgException",
    "message": "The book 12 must have at least one image",
    "status": 400,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## BookAlreadyHaveImageMaxQty

Returned when you try to add an image to a book already has the max quantity of images.

### Status

`400 Bad Request`

### Message

`The book "{name}" already has the max quantity of images`

### Example

```json
{
    "code": "BookAlreadyHaveImageMaxQty",
    "scope": "BookImgException",
    "message": "The book \"The Godfather\" already has the max quantity of images",
    "status": 400,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

# BookKeywordException

## BookKeywordDoesntExist

Returned when you try to update or delete a book keyword that doesn't exist.

### Status

`404 Not Found`

### Message

`The keyword {id} does not exist`

### Example

```json
{
    "code": "BookKeywordDoesntExist",
    "scope": "BookKeywordException",
    "message": "The keyword 12 does not exist",
    "status": 404,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## BookDoesntOwnThisKeyword

Returned when you try to update or delete a book keyword from a book doesn't own it.

### Status

`403 Forbidden`

### Message

`The keyword {id_keyword} does not belong to the book {id_book}`

### Example

```json
{
    "code": "BookDoesntOwnThisKeyword",
    "scope": "BookKeywordException",
    "message": "The keyword 46 does not belong to the book 7",
    "status": 403,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## BookMustHaveAtLeastOneKeyword

Returned when you try to delete the last keyword from a book.

### Status

`400 Bad Request`

### Message

`The book {id_book} must have at least one keyword`

### Example

```json
{
    "code": "BookMustHaveAtLeastOneKeyword",
    "scope": "BookKeywordException",
    "message": "The book 12 must have at least one keyword",
    "status": 400,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

# BookKindException

## BookKindAlreadyExists

Returned when you try to create or update a book kind with name from a kind already exists.

### Status

`409 Conflict`

### Message

`The book kind "{name}" already exists`

### Example

```json
{
    "code": "BookKindAlreadyExists",
    "scope": "BookKindException",
    "message": "The book kind \"ebook\" already exists",
    "status": 409,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## BookKindDoesntExist

Returned when you try to get, update or delete a book kind that doesn't exist.

### Status

`404 Not Found`

### Message

`The book kind {id} does not exist`

### Example

```json
{
    "code": "BookKindDoesntExist",
    "scope": "BookKindException",
    "message": "The book kind 4 does not exist",
    "status": 404,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## ThereAreLinkedBooksWithThisBookKind

Returned when you try to delete a book kind referenced by at least 1 book.

### Status

`409 Conflict`

### Message

`The book kind {id} cannot be deleted because there are books linked to this kind`

### Example

```json
{
    "code": "ThereAreLinkedBooksWithThisBookKind",
    "scope": "BookKindException",
    "message": "The book kind 2 cannot be deleted because there are books linked to this kind",
    "status": 409,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

# ImageException

## ImageNotFound

Returned when you try to get an image by filename that doesn't exist.

### Status

`404 Not Found`

### Message

`The image {filename} was not found`

### Example

```json
{
    "code": "ImageNotFound",
    "scope": "ImageException",
    "message": "The image filename.jpg was not found",
    "status": 404,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

# SavedBookException

## BookIsNotSaved

Returned when you try to delete a saved book from your account when that book isn't saved.

### Status

`404 Not Found`

### Message

`The book {id} was not saved by the user`

### Example

```json
{
    "code": "BookIsNotSaved",
    "scope": "SavedBookException",
    "message": "The book 104 was not saved by the user",
    "status": 404,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## BookAlreadySaved

Returned when you try to save a book that already is saved.

### Status

`409 Conflict`

### Message

`The book {id} is already saved by the user`

### Example

```json
{
    "code": "BookAlreadySaved",
    "scope": "SavedBookException",
    "message": "The book 69 is already saved by the user",
    "status": 409,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

# SecurityException

## InvalidJWT

Returned when you try to request a protected endpoint with an invalid JWT token.

### Status

`401 Unauthorized`

### Message

`Invalid JWT token`

### Example

```json
{
    "code": "InvalidJWT",
    "scope": "SecurityException",
    "message": "Invalid JWT token",
    "status": 401,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## MissingJWT

Returned when you try to request a protected endpoint without JWT token.

### Status

`401 Unauthorized`

### Message

`JWT token not provided`

### Example

```json
{
    "code": "MissingJWT",
    "scope": "SecurityException",
    "message": "JWT token not provided",
    "status": 401,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## MissingCSRF

Returned when you try to request a protected endpoint without CSRF token.

### Status

`400 Bad Request`

### Message

`CSRF token not provided`

### Example

```json
{
    "code": "MissingCSRF",
    "scope": "SecurityException",
    "message": "CSRF token not provided",
    "status": 400,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

## InvalidCSRF

Returned when you try to request a protected endpoint with an invalid CSRF token.

### Status

`400 Bad Request`

### Message

`Invalid CSRF token`

### Example

```json
{
    "code": "InvalidCSRF",
    "scope": "SecurityException",
    "message": "Invalid CSRF token",
    "status": 400,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>

# UserException

## UserAlreadyExists

Returned when you try to create or update an user with name from an user already exists.

### Status

`409 Conflict`

### Message

`This user already exists`

### Example

```json
{
    "code": "UserAlreadyExists",
    "scope": "UserException",
    "message": "This user already exists",
    "status": 409,
    "timestamp": "2024-07-23T15:33:58.758304+00:00"
}
```

<br/>
