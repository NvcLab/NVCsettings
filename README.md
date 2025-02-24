# Table of Contents
- [Installation](#installation)
- [Supported Configuration File Formats](#supported-configuration-file-formats)
- [Configuration File Examples](#configuration-file-examples)
  - [YAML Example](#yaml-example)
  - [JSON Example](#json-example)
  - [TOML Example](#toml-example)
  - [Dotenv Example](#dotenv-example)
- [Schema File Example](#schema-file-example)
  - [YAML Schema Example](#yaml-schema-example)
  - [JSON Schema Example](#json-schema-example)
  - [TOML Schema Example](#toml-schema-example)
- [Usage Example](#usage-example)
- [Important Usage Notes](#important-usage-notes)

## Installation

To install the required dependencies, make sure you have Python installed. You can use `uv` to create and manage your virtual environment and install dependencies. For detailed instructions, refer to the [official UV installation guide](https://docs.astral.sh/uv/getting-started/installation/).

To install the dependencies and create the environment, run the following command:

```sh
uv sync
```

## Supported Configuration File Formats

The software supports the following configuration file formats:
- YAML (`.yaml`, `.yml`)
- JSON (`.json`)
- TOML (`.toml`)

These formats are used to define the configuration settings for the application and are interchangeable based on user preference.

## Configuration File Examples

### YAML Example

Create a `config.yaml` file with the following content:

```yaml name=config.yaml
app_name: MyApp
app:
  app_version: "1.0.0"
  example_key:
    key: "value"
logging:
  console:
    enabled: true
    level: DEBUG
    format: "<green>{time}</green> | <level>{level: <8}</level> | {message}"
    time_format: "YYYY-MM-DD HH:mm:ss.SSS"
  file:
    enabled: true
    file_path: "logs/app.log"
    level: DEBUG
    format: "{time} | {level} | {message}"
    time_format: "YYYY-MM-DD HH:mm:ss.SSS"
    rotation: "10 MB"
    compression: "zip"
```

### JSON Example

<details>
<summary>Create a <code>config.json</code> file with the following content:</summary>

```json name=config.json
{
  "app_name": "MyApp",
  "app": {
    "app_version": "1.0.0",
    "example_key": {
      "key": "value"
    }
  },
  "logging": {
    "console": {
      "enabled": true,
      "level": "DEBUG",
      "format": "<green>{time}</green> | <level>{level: <8}</level> | {message}",
      "time_format": "YYYY-MM-DD HH:mm:ss.SSS"
    },
    "file": {
      "enabled": true,
      "file_path": "logs/app.log",
      "level": "DEBUG",
      "format": "{time} | {level} | {message}",
      "time_format": "YYYY-MM-DD HH:mm:ss.SSS",
      "rotation": "10 MB",
      "compression": "zip"
    }
  }
}
```
</details>

### TOML Example

<details>
<summary>Create a <code>config.toml</code> file with the following content:</summary>

```toml name=config.toml
app_name = "MyApp"

[app]
app_version = "1.0.0"

[app.example_key]
key = "value"

[logging.console]
enabled = true
level = "DEBUG"
format = "<green>{time}</green> | <level>{level: <8}</level> | {message}"
time_format = "YYYY-MM-DD HH:mm:ss.SSS"

[logging.file]
enabled = true
file_path = "logs/app.log"
level = "DEBUG"
format = "{time} | {level} | {message}"
time_format = "YYYY-MM-DD HH:mm:ss.SSS"
rotation = "10 MB"
compression = "zip"
```
</details>

### Dotenv Example

Create a `.env` file with the following content:

```dotenv name=.env
SECRET_KEY="your-secret-key"
DATABASE_URL="postgres://user:password@localhost:5432/mydatabase"
```

## Schema File Example

### YAML Schema Example

Create a `schema.yaml` file with the following content:

```yaml name=schema.yaml
application:
  app_name: "str"
  app:
    app_version: "str"
    example_key:
      key: "str"
  logging:
    console:
      enabled: "bool"
      level: "str"
      format: "str"
      time_format: "str"
    file:
      enabled: "bool"
      file_path: "str"
      level: "str"
      format: "str"
      time_format: "str"
      rotation: "str"
      compression: "str"

secrets:
  SECRET_KEY: "str"
  DATABASE_URL: "str"
```

### JSON Schema Example

<details>
<summary>Create a <code>schema.json</code> file with the following content:</summary>

```json name=schema.json
{
  "application": {
    "app_name": "str",
    "app": {
      "app_version": "str",
      "example_key": {
        "key": "str"
      }
    },
    "logging": {
      "console": {
        "enabled": "bool",
        "level": "str",
        "format": "str",
        "time_format": "str"
      },
      "file": {
        "enabled": "bool",
        "file_path": "str",
        "level": "str",
        "format": "str",
        "time_format": "str",
        "rotation": "str",
        "compression": "str"
      }
    }
  },
  "secrets": {
    "SECRET_KEY": "str",
    "DATABASE_URL": "str"
  }
}
```
</details>

### TOML Schema Example

<details>
<summary>Create a <code>schema.toml</code> file with the following content:</summary>

```toml name=schema.toml
[application]
app_name = "str"

[application.app]
app_version = "str"

[application.app.example_key]
key = "str"

[application.logging.console]
enabled = "bool"
level = "str"
format = "str"
time_format = "str"

[application.logging.file]
enabled = "bool"
file_path = "str"
level = "str"
format = "str"
time_format = "str"
rotation = "str"
compression = "str"

[secrets]
SECRET_KEY = "str"
DATABASE_URL = "str"
```
</details>

## Usage Example

Create a `main.py` file with the following content to use the configuration and logging setup:

```python name=main.py
from loguru import logger

from settings import get_app_settings, configure_logging

schema_file = "./settings/schema.yaml"
config_file = "./settings/config.yaml"
dotenv_file = "./settings/.env"

settings = get_app_settings(config_file, schema_file, dotenv_file)
configure_logging(settings.application.logging)

logger.info(f"Application name: {settings.application.app_name}")
logger.info(f"Application version: {settings.application.app['app_version']}")
logger.info(f"Example key: {settings.application.app['example_key']['key']}")

logger.info(f"Secret: {settings.secrets.secret}")
```

## Important Usage Notes

- **Nesting in YAML**: When using nested structures in YAML, access the nested values properly. For example, if you have a nested key under `app`, you access it using `settings.application.app['example_key']['key']`.
- **Environment Variables**: Ensure your `.env` file is correctly formatted with key-value pairs. The `SECRET_KEY` and `DATABASE_URL` in the example should be replaced with your actual secret values.
- **Validation**: The schema file (`schema.yaml`) helps in validating the structure and types of your configuration files to prevent runtime errors.