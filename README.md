<div align="center">
    <h1>
        <img src="chatterbox/static/favicon.png" width="200" alt="Logo Icon"/>
    </h1>
    <p>Enables real-time chat conversations among users.<br><a href="https://chatterbox-demo.onrender.com/">https://chatterbox-demo.onrender.com/</a><br>Written in Python/Django</p>
    <a href="https://github.com/KafetzisThomas/Chatterbox/actions/workflows/tests.yml">
        <img src = "https://github.com/KafetzisThomas/Chatterbox/actions/workflows/tests.yml/badge.svg" alt="Run Tests"/>
    </a>
</div>

---

## Features

- [X] View and modify your profile details, including your avatar, username and password.
- [X] Create private 1-on-1 conversations with other users.
- [X] Users can send:
    - [X] Text
    - [ ] Files
    - [X] Images
- [X] Allow users to delete entire conversations
- [x] Detect links and add an anchor tag to them
- [X] Receive email notifications for mentions

## Purpose

The primary goal of this project is to **provide an open-source chat application that anyone can use, modify, and learn from**. While the deployed app is available for use, the main intention is not to attract active users or compete with major chat applications. Instead, this project aims to share the code, primarily written in Django, with developers who might find it helpful for building similar real-time communication tools or for personal projects.

During the development and deployment of this project, I faced several challenges, particularly with **CSRF verification errors**. These issues led me to create a Django forum post where I detailed the problem and finally the solution I found. I hope this resource proves helpful for others encountering similar deployment issues:

https://forum.djangoproject.com/t/forbidden-403-csrf-verification-failed-request-aborted-error-encountered-in-production/34354

If you find this project interesting, helpful, or inspiring, please consider giving it a `star`, `following`, or even `donating` to support further development and improvements.

## Django Models
Here is a graphical representation of the Django models used in this project:

<div align="center"><img src="https://github.com/user-attachments/assets/3e8d8f5a-7d23-496d-bf96-b6606ea045cc" alt="Django Models Graph" width="500"/></div>

## Setup for Local Development

### Set up Virtual Environment

```bash
➜ cd path/to/root/directory
$ python3 -m venv env/
$ source env/bin/activate
```

### Install Dependencies

```bash
$ pip3 install -r requirements.txt
```

### Create Enviroment Variable file

```bash
$ touch main/.env
$ nano main/.env
```

Add the following environment variables (modify as needed):
```bash
➜ SECRET_KEY="example_secret_key"  # https://stackoverflow.com/a/57678930
➜ DEBUG=True  # For development
```

Save changes and close the file.

### Migrate Database

```bash
$ python3 manage.py migrate
```

### Run Django Server
```bash
$ python3 manage.py runserver
```

Now you can access the website at `http://127.0.0.1:8000/` or `http://localhost:8000/`.

## Run Tests

```bash
➜ cd path/to/root/directory
$ python3 manage.py test users.tests chatterbox.tests
```

## Contributing Guidelines for Chatterbox

### Pull Requests
When submitting a pull request, please keep these points in mind:

* **Simplicity**: Keep your changes straightforward and focused. Complex changes are harder to review and integrate.

* **Avoid Non-Standard Libraries**: Whenever possible, refrain from adding new non-standard libraries. If your idea necessitates one, kindly discuss it first by opening an issue. This helps in evaluating the necessity and compatibility of the library.

* **Ensure It Runs**: Before submitting a pull request, ensure that your code runs without errors and adheres to the project's coding standards.

* **Pass All Tests**: Make sure all existing [tests](#run-tests) pass and add new tests as necessary. Pull requests will not be merged unless all tests pass successfully.

### Filing Bug Reports and Submitting Pull Requests
If you encounter a bug, please follow these steps to report it:

* **Bug Reports**: File bug reports on the [GitHub Issues](https://github.com/KafetzisThomas/Chatterbox/issues) page.
* **Pull Requests**: Open pull requests on the [GitHub Pull Requests](https://github.com/KafetzisThomas/Chatterbox/pulls) page.

Before contributing, please review the [License](https://github.com/KafetzisThomas/Chatterbox/blob/main/LICENSE) to understand the terms and conditions governing the use and distribution of Chatterbox.

Thank you for your interest in improving Chatterbox!
