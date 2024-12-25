# robyn blog

## feathers

- user register
- user login
- jwt
- post crud sqlalchemy
- page

## folder tree

```
├── README.md
├── database.py
├── main.py
├── pyproject.toml
├── security.py
└── uv.lock
```

## install and start server

<details>
  <summary>pip</summary>
  <pre><code> 
python -m venv .venv
source .venv/bin/activate
pip install .
robyn main.py
  </code></pre>
</details>

## install uv

[uv](https://github.com/astral-sh/uv)

```sh
pipx install uv
```

## install

```sh
uv sync  # install packages from pyproject.toml, sync from uv.lock
```

## start server

```sh
uv run robyn main.py # --dev
```
