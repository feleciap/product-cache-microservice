from loguru import logger

logger.add("logs.log", rotation="500 KB", level="INFO")