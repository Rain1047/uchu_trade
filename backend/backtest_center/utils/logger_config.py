# utils/logger_config.py

import logging


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    配置日志器，避免重复

    Args:
        name: 日志器名称
        level: 日志级别

    Returns:
        logging.Logger: 配置好的日志器
    """
    logger = logging.getLogger(name)

    # 如果已经有处理器，说明已经配置过，直接返回
    if logger.handlers:
        return logger

    # 设置日志级别
    logger.setLevel(level)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    # 添加处理器
    logger.addHandler(console_handler)

    return logger
