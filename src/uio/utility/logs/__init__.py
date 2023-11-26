"""
.. include:: ../../../../documentation/utility/logs/index.md
"""

import os

debugMode: bool = False
"""
Flag for enabling debug log. If set to `True`, then debug logging format
will be enabled, and more details will be printed to the log.
"""

if "UIO_EXOPLANET_GROUP_DEBUG" in os.environ:
    debugModeValue: str = os.environ["UIO_EXOPLANET_GROUP_DEBUG"].lower()
    if (
        debugModeValue != "0"
        and
        debugModeValue != "no"
        and
        debugModeValue != "off"
        and
        debugModeValue != "false"
        and
        debugModeValue != "disable"
    ):
        debugMode = True
