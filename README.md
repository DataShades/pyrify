# Pyrify

A CLI tool for database sanitization

## Installation

```bash
pip install pyrify
```

## Initialize the sanitize config

### Initialize from database
By providing the database URI, the tool will automatically generate a sanitize config file.
Currently, the tool supports PostgreSQL, MySQL (with `pymysql`), and SQLite.


```sh
# PostgreSQL
pyrify init -d "postgresql://user:pass@localhost/db_name" > config.yml

# MySQL
pyrify init -d "mysql+pymysql://user:pass@localhost/db_name" > config.yml

# SQLite
pyrify init -d "sqlite:///db-sanitize.db" > config.yml
```

### Use sanitize config template

You can use a template to generate the sanitize config file.

```sh
pyrify template -t ckan_211 > config.yml
```

To see the available templates, run:

```sh
pyrify template
```

## Configure the sanitize config

The `init` command will create a config file with the following structure:

```yaml
table_name:
  columns:
    column_name1: '~'
    column_name2: '~'
    column_name3: '~'
```

If you don't need to sanitize a table or a column, you can remove it from the config file.

There are 3 key options:

- `clean`: This will clean the table (remove all data).
- `drop`: This will drop the table.
- `columns`: This will apply a specific sanitization strategy to the column.

Example:

```yaml
activity:
  clean: true

unused_table:
  drop: true

user:
  columns:
    plugin_extras:
      strategy: json_update
      kwargs:
        columns:
          test: fake_password
    last_active: nullify
    fullname: fake_fullname
    image_url: nullify
    email: fake_email
    name: fake_username
    password: fake_password
    about: fake_text

```

### Strategies

The following strategies are available:

- `fake_username`: This will generate a fake username.
- `fake_fullname`: This will generate a fake full name.
- `fake_text`: This will generate a fake text.
- `fake_email`: This will generate a fake email.
- `fake_password`: This will generate a fake password.
- `fake_phone_number`: This will generate a fake phone number.
- `fake_address`: This will generate a fake address.
- `nullify`: This will set the column to `NULL`.
- `json_update`: This will update the JSON key with the new value.

## Sanitize the database

Below are some examples of how to sanitize the database.

The `-d` option is the database URI and the `-c` option is the path to the sanitize config file.

```sh
pyrify sanitize -d "postgresql://root:root@localhost/db_name" -c config.yml
pyrify sanitize -d "mysql+pymysql://root:root@127.0.0.1:3306/db_name" -c config.yml
```

