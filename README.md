# Pyrify

A CLI tool for database sanitization

## Installation

```bash
pip install pyrify
```

## Initialize the sanitize config

### Postgres

By providing the database URI, the tool will automatically generate a sanitize config file.

```sh
pyrify init -d "postgresql://user:pass@localhost/db_name" > config.yml
```

### MySQL

```sh
pyrify init -d "mysql+pymysql://user:pass@localhost/db_name" > config.yml
```

## Configure the sanitize config

The `init` command will create a config file with the following structure:

```yaml
```

You have to specify the tables and columns that you want to sanitize. If you 
don't need to sanitize a table or a column, you can remove it from the config file.
