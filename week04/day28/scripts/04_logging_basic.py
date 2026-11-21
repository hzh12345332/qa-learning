import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logging.info("开始执行")
logging.warning("配置缺失，用默认值")
logging.error("请求失败")