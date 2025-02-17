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
