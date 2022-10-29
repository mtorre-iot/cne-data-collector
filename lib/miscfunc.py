#
# TTG Global - 10/06/2022
#
# --------------------------------------------------------------------------- #
import logging


def text_to_log_level (str):
    if str=="INFO":
        return logging.INFO
    if str=="DEBUG":
        return logging.DEBUG
    if str=="WARN":
        return logging.WARN
    if str=="ERROR":
        return logging.ERROR
    return logging.DEBUG
