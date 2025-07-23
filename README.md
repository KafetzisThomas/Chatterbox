<p align="center">
    <img src="chatterbox/static/favicon.png" width="200" alt="Logo Icon"/><br>
    Enables real-time chat conversations among users.<br>
    Written in Python/Django
</p>

## Features

- [X] View and modify your profile details, including your avatar, username and password.
- [X] Create private 1-on-1 conversations with other users.
- [X] Users can send:
    - [X] Text
    - [ ] Files
    - [X] Images
- [X] Allow users to delete entire conversations
- [X] Remove individual messages in conversations
- [x] Detect links and add an anchor tag to them
- [X] Receive email notifications for mentions

## Notice

During the development and deployment of this project I faced several challenges, particularly with **CSRF verification errors**. These issues led me to create a Django forum post where I detailed the problem and finally the solution I found. I hope this resource proves helpful for others encountering similar deployment issues:

https://forum.djangoproject.com/t/forbidden-403-csrf-verification-failed-request-aborted-error-encountered-in-production/34354

If you find this project interesting, helpful or inspiring, please consider giving it a `star` or `following` to support further development and improvements.

## Django Models
Here is a graphical representation of the Django models used in this project:

<div align="center"><img src="https://github.com/user-attachments/assets/3e8d8f5a-7d23-496d-bf96-b6606ea045cc" alt="Django Models Graph" width="500"/></div>

## Setup for Local Development

### Install uv

```bash
➜ cd path/to/root/directory
$ pip install uv
```

### Create Enviroment Variable file

```bash
$ touch main/.env
$ nano main/.env
```

Add the following (adjust as needed):
```bash
# Django settings
➜ SECRET_KEY="example_secret_key"  # https://stackoverflow.com/a/57678930
➜ ALLOWED_HOSTS="localhost,127.0.0.1"
➜ CSRF_TRUSTED_ORIGINS="http://localhost:8001"
➜ DEBUG=True  # For development

# Email settings
➜ EMAIL_HOST_USER="example_email_host"
➜ EMAIL_HOST_PASSWORD="example_email_password"
```

Save changes and close the file.

### Migrate Database

```bash
$ uv run manage.py migrate
```

### Run Django Server
```bash
$ uv run manage.py runserver
```

Now you can access the website at `http://127.0.0.1:8000/` or `http://localhost:8000/`.

## Run Tests

```bash
$ uv run manage.py test
```

## Demo Image

<img width="1919" height="1079" alt="Screenshot 2025-07-23 121108" src="https://github.com/user-attachments/assets/425d0fd7-93d7-48c9-8c3b-5f2f631ee74f" />

## Contributing Guidelines

### Pull Requests
* **Simplicity**: Keep changes focused and easy to review.
* **Libraries**: Avoid adding non-standard libraries unless discussed via an issue.
* **Testing**: Ensure code runs error-free, passes all tests, and meets coding standards.

### Bug Reports
* Report bugs via GitHub Issues.
* Submit pull requests via GitHub Pull Requests.

Thank you for supporting Chatterbox!
