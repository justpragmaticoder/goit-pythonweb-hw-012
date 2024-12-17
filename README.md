# goit-pythonweb-hw-10

Make sure you have [Docker Engine](https://docs.docker.com/engine/install/) installed first

### Install dependencies (3.10 python is used)
```bash
poetry install
```

### Plz, fill .env file this should be placed in the root folder
You can check .env-example file and see which env variables should be filled for correct launch.

### Run docker compose

```bash
docker-compose up -d
```

There are already commited migrations for the demonstration

```shell
alembic upgrade head
```

Open in browser SWAGGER doc: [link](http://127.0.0.1:8000/docs)

To check db connection works you can use SWAGGER operation GET `/api/health`

### Tests

Run pytests and generate the test coverage report

```bash
pytest --cov=src tests/ --cov-report=html
```

Check tests coverage HTML
[link](htmlcov/index.html)

Check the doc file HTML
[link](docs/_build/html/index.html)