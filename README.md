<h1 align="center">
    <img src="https://res.cloudinary.com/dd1gccg4f/image/upload/v1721312522/frigattobooks.png" width="200"/>
    <br/>
    <p style="font-size: 30px">Frigatto Books REST API</p>
</h1>

<p align="center">
    This repository contains the REST API for the <b>Frigatto Books</b> project. Built with Flask, it provides endpoints for managing books, genres, types and more. The API uses JWT authentication and supports CORS for secure cross-origin requests.
</p>

> ⚠️ This API depends on [Frigatto Books Database](https://github.com/Alberto-Frigatto/frigatto-books-database)

# Table of contents

- [Installation](#installation)
- [Endpoints](#endpoints)
- [Errors](#errors)
- [License](#license)


# Installation

Clone this repository

```bash
git clone https://github.com/Alberto-Frigatto/frigatto-books-rest-api.git
```

Go to repository where you've cloned it

```bash
cd path/to/repository/frigatto-books-rest-api
```

Build the docker image

```bash
docker build -t frigatto_books_rest_api .
```

Finally, create a container providing the following configurations:

### Env variables

- SECRET_KEY - [Flask's secret key](https://flask.palletsprojects.com/en/3.0.x/config/#SECRET_KEY)
- DB_USER (optional) - Database user's name (if not provided, it'll be `root`)
- DB_PWD - Database user's password
- DB_HOST - [Frigatto Books Database](https://github.com/Alberto-Frigatto/frigatto-books-database)'s IP address
- JWT_SECRET_KEY - [Secret key for JWT](https://flask-jwt-extended.readthedocs.io/en/stable/options.html#jwt-secret-key)
- ALLOW-ORIGIN (optional) - Url for your front-end server (if not provided, it'll be `http://127.0.0.1:5500`)

### Volumes

- Attach a docker volume in `/usr/src/app/uploads` to persist images even container is deleted

### Ports

- Map the container's `5000` port to your pc's `5000` port

Assuming the [Frigatto Books Database](https://github.com/Alberto-Frigatto/frigatto-books-database) is running at `172.17.0.2`

```bash
docker run --name frigatto_books_rest_api_container \
-v frigatto-books-data:/usr/src/app/uploads \
-e SECRET_KEY=your_secret_key \
-e JWT_SECRET_KEY=your_secret_key \
-e DB_PWD=your_password \
-e DB_HOST=172.17.0.2 \
-p 5000:5000 \
frigatto_books_rest_api
```

After that, the api will be visible at `http://127.0.0.1:5000` or `http://localhost:5000`

# Endpoints

To see all api endpoints, check our [docs about them](./docs/endpoints.md).

# Errors

To see all api errors, check our [docs about them](./docs/errors.md).

# License

[MIT](./LICENSE.md) - Alberto Frigatto, 2024
