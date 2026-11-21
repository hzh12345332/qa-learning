# 06_logging_pitfalls.py
import logging
import sys

FMT = "[%(levelname)s] %(name)s: %(message)s"


def exp1_basicconfig_once():
    """坑1:第二次 basicConfig 不生效"""
    logging.basicConfig(level=logging.DEBUG, format=FMT, stream=sys.stdout)
    logging.debug("1) 第一次配 DEBUG → 能出来")
    logging.basicConfig(level=logging.WARNING, format=FMT, stream=sys.stdout)
    logging.debug("2) 本该消失，但还在出")
    logging.info("3) INFO 也在出 → level 还是 DEBUG(10)")


def exp2_duplicate_handler():
    """坑2:root 多挂一个 handler → 每行出两次"""
    logging.basicConfig(level=logging.INFO, format=FMT, stream=sys.stdout)
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter(FMT))
    logging.getLogger().addHandler(h)
    logging.info("这条一模一样地出现两次")


def exp3_propagate():
    """坑3:propagate=True 冒泡到 root → 每行出两次"""
    logging.basicConfig(level=logging.INFO, format=FMT, stream=sys.stdout)
    logger = logging.getLogger("qa")
    logger.setLevel(logging.INFO)
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter(FMT))
    logger.addHandler(h)
    print("qa.propagate =", logger.propagate)
    logger.info("这条出现两次：自己的 handler 一次 + 冒泡到 root 一次")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": exp1_basicconfig_once,
     "2": exp2_duplicate_handler,
     "3": exp3_propagate}.get(which, exp1_basicconfig_once)()