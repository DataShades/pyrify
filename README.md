# Pyrify

A CLI tool for database sanitization

## Installation

### Using pip (recommended for virtual environments)

```bash
pip install pyrify
```

### Using pipx (recommended for global installation)

[pipx](https://pipx.pypa.io/stable/) allows you to install the tool globally without affecting your system Python:

```bash
pipx install pyrify
```

## Quick Start

Here's how to get started with Pyrify in just a few steps:

### Option 1: Using pip in a virtual environment

1. Create and activate a virtual environment
2. Install Pyrify and generate a configuration file from a template
3. Sanitize your database

```bash
pip install pyrify
pyrify template -t ckan_211 > config.yaml
pyrify sanitize -d "postgresql://user:pass@localhost/db_name" -c config.yaml
```

### Option 2: Using pipx (global installation)

If you prefer not to create a virtual environment and want to install the package globally, use pipx:

```bash
pipx install pyrify
pyrify template -t ckan_211 > config.yaml
pyrify sanitize -d "postgresql://user:pass@localhost/db_name" -c config.yaml
```

## Initialize the Sanitization Config

### Option 1: Initialize from Database

By providing the database URI, the tool will automatically generate a sanitization config file.
Currently, the tool supports PostgreSQL, MySQL (with `pymysql`), and SQLite.

```bash
# PostgreSQL
pyrify init -d "postgresql://user:pass@localhost/db_name" > config.yml

# MySQL
pyrify init -d "mysql+pymysql://user:pass@localhost/db_name" > config.yml

# SQLite
pyrify init -d "sqlite:///db-sanitize.db" > config.yml
```

### Option 2: Use a Sanitization Config Template

Templates are **pre-defined sanitization config** files for common platforms like CKAN, Drupal, and more to come.

Check the [templates](./pyrify/templates) directory for available templates, or run the following command to see all available templates:

```bash
pyrify template
```

You can use a template to generate the sanitization config file:

```bash
pyrify template -t ckan_211 > config.yml
```

## Configure the Sanitization Config

The `init` command will create a config file with the following structure:

```yaml
table_name:
  columns:
    column_name1: '~'
    column_name2: '~'
    column_name3: '~'
```

If you don't need to sanitize a table or column, you can remove it from the config file.

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

### Available Strategies

The following sanitization strategies are available:

- `fake_username`: Generates a fake username.
- `fake_fullname`: Generates a fake full name.
- `fake_text`: Generates fake text content.
- `fake_email`: Generates a fake email address.
- `fake_password`: Generates a fake password.
- `fake_phone_number`: Generates a fake phone number.
- `fake_address`: Generates a fake address.
- `nullify`: Sets the column value to `NULL`.
- `json_update`: Updates JSON keys with new values.

## Sanitize the Database

Below are examples of how to sanitize your database.

Use the `-d` option to specify the database URI and the `-c` option for the path to the sanitization config file:

```bash
pyrify sanitize -d "postgresql://root:root@localhost/db_name" -c config.yml
pyrify sanitize -d "mysql+pymysql://root:root@127.0.0.1:3306/db_name" -c config.yml
```
