import logging
import sys


def setup_logger(name="qa", logfile=None, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False            # ← 不往父 logger 传（防重复）

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    console = logging.StreamHandler(sys.stdout)      # ① 控制台
    console.setFormatter(fmt)
    logger.addHandler(console)

    if logfile:                                      # ② 文件（可选）
        fh = logging.FileHandler(logfile, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


logger = setup_logger("qa.day28", "out.log", logging.DEBUG)
logger.debug("细节:userId=1")
logger.info("用例开始")
logger.warning("重试了一次")
logger.error("断言失败")