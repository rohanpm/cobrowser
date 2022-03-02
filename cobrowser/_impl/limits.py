import logging
import os
import resource

LOG = logging.getLogger("cobrowser")

MEMLIMIT_MB = int(os.getenv("COBROWSER_MEMLIMIT_MB", "1024"))


def memlimit():
    if MEMLIMIT_MB == 0:
        return

    usage = resource.getrusage(resource.RUSAGE_SELF)
    # Note: RSS is returned in KB, RLIMIT_AS uses bytes.
    rss = usage.ru_maxrss * 1024
    bumpto = rss + 1024 * 1024 * MEMLIMIT_MB
    try:
        resource.setrlimit(resource.RLIMIT_AS, (bumpto, bumpto))
    except Exception:
        LOG.exception("Failed setting RLIMIT_AS to %s", bumpto)
