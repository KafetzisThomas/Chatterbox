<div align="center">
    <img src="static/favicon.png" width="150"/><br>
    <p><strong>Chatbox: </strong>Exchange messages between users.<br>Written in Python/Django</p>
</div>

> [!NOTE]
> During development and deployment I encountered **CSRF verification errors** and documented the issue and fix in a forum post.
> This may help others facing similar production issues:
> <https://forum.djangoproject.com/t/forbidden-403-csrf-verification-failed-request-aborted-error-encountered-in-production/34354>

## Features

- [X] Private 1 on 1 conversations with other users
- [X] Send `links` and `images` with low latency
- [X] Delete individual messages or entire conversations

## Database Schema

![Database Schema](/assets/db_schema.png)

## Usage

### Local Development

First install `uv` and sync the project dependencies:

```bash
cd path/to/root/directory
pip install uv
uv sync
uv sync --extra dev  # for devs only
```

Migrate database:

```bash
uv run manage.py migrate
```

Run Django server:

```bash
uv run manage.py runserver
```

Access web application at `http://127.0.0.1:8000` or `http://localhost:8000`.

## Run Tests

```bash
uv run manage.py test
```

## Demo Image

![Screenshot 2025-07-23 121108](https://github.com/user-attachments/assets/425d0fd7-93d7-48c9-8c3b-5f2f631ee74f)

## Contributing Guidelines

### Pull Requests

- **Simplicity**: Keep changes focused and easy to review.
- **Libraries**: Avoid adding non-standard libraries unless discussed via an issue.
- **Testing**: Ensure code runs error-free, passes all tests, and meets coding standards.

### Bug Reports

- Report bugs via GitHub Issues.
- Submit pull requests via GitHub Pull Requests.

Thank you for supporting Chatbox!
