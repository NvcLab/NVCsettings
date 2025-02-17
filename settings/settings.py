import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional, Any, Dict

import toml
import yaml
from loguru import logger
from pydantic_settings import BaseSettings


class ConfigurationFileLoader:
    _cache: Dict[Path, dict] = {}

    @staticmethod
    def load(file_path: Path) -> dict:
        if file_path in ConfigurationFileLoader._cache:
            cache_entry = ConfigurationFileLoader._cache[file_path]
            file_mtime = file_path.stat().st_mtime
            if cache_entry["mtime"] == file_mtime:
                return cache_entry["data"]

        try:
            config = ConfigurationFileLoader._read(file_path)
            ConfigurationFileLoader._cache[file_path] = {"data": config, "mtime": file_path.stat().st_mtime}
            return config
        except FileNotFoundError:
            logger.warning(f"Configuration file {file_path} not found.")
            raise
        except ValueError as ve:
            logger.error(f"Invalid file format for {file_path}: {ve}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error while loading file {file_path}: {e}")
            raise

    @staticmethod
    def _read(file_path: Path) -> dict:
        file_suffix = file_path.suffix.lower()
        try:
            with open(file_path, 'r') as file:
                if file_suffix in [".yaml", ".yml"]:
                    return yaml.safe_load(file)
                elif file_suffix == ".json":
                    return json.load(file)
                elif file_suffix == ".toml":
                    return toml.load(file)
                else:
                    raise ValueError(f"Unsupported configuration file format: {file_suffix}")
        except Exception as e:
            logger.exception(f"Error reading file {file_path}: {e}")
            raise


class ConfigurationValidator:
    TYPE_MAPPING = {
        "str": str,
        "bool": bool,
        "int": int,
        "float": float,
        "list": list,
        "dict": dict,
        "NoneType": type(None),
        "tuple": tuple,
    }

    @staticmethod
    def validate(data: dict, schema: dict) -> None:
        for key, expected in schema.items():
            if key not in data:
                raise ValueError(f"Missing required configuration field: {key}")
            ConfigurationValidator._validate_type(data[key], expected, key)

    @staticmethod
    def _validate_type(value: Any, expected: Any, key: str) -> None:
        if isinstance(expected, str):
            expected_type = ConfigurationValidator.TYPE_MAPPING.get(expected)
            if expected_type is None:
                raise ValueError(f"Unsupported expected type: {expected} for field {key}")
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"Incorrect type for field '{key}', "
                    f"expected {expected_type.__name__} but got {type(value).__name__}."
                )
        elif isinstance(expected, dict):
            if not isinstance(value, dict):
                raise TypeError(f"Incorrect type for field '{key}', expected dict.")
            ConfigurationValidator.validate(value, expected)
        else:
            raise ValueError(f"Invalid schema definition for field {key}")


class ApplicationConfig(BaseSettings):
    class Config:
        extra = "allow"

    @classmethod
    def load_from_file(cls, config_file_path: str, schema: Optional[dict] = None) -> "ApplicationConfig":
        file_path = Path(config_file_path)
        config_data = ConfigurationFileLoader.load(file_path)
        if schema:
            ConfigurationValidator.validate(config_data, schema)
        if 'logging' in config_data and not isinstance(config_data['logging'], dict):
            raise ValueError("Invalid format for 'logging', expected a dictionary.")

        return cls(**config_data)


class SecretConfig(BaseSettings):
    class Config:
        env_file_encoding = "utf-8"
        extra = "allow"

    @classmethod
    def validate_against_schema(cls, data: Dict[str, Any], schema: dict) -> None:
        ConfigurationValidator.validate(data, schema)


class AppSettings:
    application: ApplicationConfig
    secrets: SecretConfig

    def __init__(self, config_file_path: Optional[str] = None, schema_file_path: Optional[str] = None, dotenv_file_path: Optional[str] = None):
        self.application = self._load_application_config(config_file_path, schema_file_path)
        self.secrets = SecretConfig(_env_file=dotenv_file_path)
        self._validate_secrets(schema_file_path)

    def _load_application_config(self, config_file_path: Optional[str],
                                 schema_file_path: Optional[str]) -> ApplicationConfig:
        if config_file_path:
            app_schema = self._load_schema_section(schema_file_path, "application")
            return ApplicationConfig.load_from_file(config_file_path, schema=app_schema)
        return ApplicationConfig()

    def _load_schema_section(self, schema_file_path: Optional[str], section: str) -> Optional[dict]:
        if schema_file_path and Path(schema_file_path).exists():
            full_schema = ConfigurationFileLoader.load(Path(schema_file_path))
            if section in full_schema:
                return full_schema[section]
            else:
                raise KeyError(f"The schema does not contain the '{section}' section.")
        return None

    def _validate_secrets(self, schema_file_path: Optional[str]) -> None:
        schema = self._load_schema_section(schema_file_path, "secrets")
        if schema:
            try:
                SecretConfig.validate_against_schema(self.secrets.dict(), schema)
            except Exception as e:
                logger.error("Secret configuration validation failed: " + str(e))
                raise


@lru_cache(maxsize=None)
def get_app_settings(config_file_path: Optional[str] = None, schema_file_path: Optional[str] = None, dotenv_file_path: Optional[str] = None) -> AppSettings:
    return AppSettings(config_file_path, schema_file_path, dotenv_file_path)


def configure_logging(config: dict) -> None:
    logger.remove()

    if not config:
        logger.warning("No logging configuration provided. Using default settings.")

    if 'console' in config:
        _configure_console_logging(config.get("console", {}))
    else:
        logger.warning("Console logging configuration not found, skipping console logging setup.")

    if 'file' in config:
        _configure_file_logging(config.get("file", {}))
    else:
        logger.warning("File logging configuration not found, skipping file logging setup.")


def _configure_console_logging(console_config: dict) -> None:
    if console_config.get("enabled", False):
        console_format = console_config.get(
            "format",
            "<green>{time}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        console_level = console_config.get("level", "DEBUG").upper()
        time_format = console_config.get("time_format", "YYYY-MM-DD HH:mm:ss.SSS")

        console_format = console_format.replace("{time}", "{time:" + time_format + "}")

        logger.add(
            lambda msg: print(msg, end=""),
            format=console_format,
            level=console_level,
            colorize=True,
        )
    else:
        logger.warning("Console logging is disabled in the configuration.")


def _configure_file_logging(file_config: dict) -> None:
    if file_config.get("enabled", False):
        file_path = file_config.get("file_path", "app.log")
        file_format = file_config.get("format", "{time} | {level} | {message}")
        file_level = file_config.get("level", "DEBUG").upper()
        rotation = file_config.get("rotation", "10 MB")
        compression = file_config.get("compression", "zip")
        time_format = file_config.get("time_format", "YYYY-MM-DD HH:mm:ss.SSS")

        file_format = file_format.replace("{time}", "{time:" + time_format + "}")

        log_folder = os.path.dirname(file_path)
        if log_folder and not os.path.exists(log_folder):
            os.makedirs(log_folder)

        logger.add(
            file_path,
            format=file_format,
            level=file_level,
            rotation=rotation,
            compression=compression,
        )
    else:
        logger.warning("File logging is disabled in the configuration.")