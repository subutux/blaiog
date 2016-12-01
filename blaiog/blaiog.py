import asyncio
import functools
import signal, sys
import logging
log = logging.getLogger('trapdoor')
log.addHandler(logging.NullHandler())
import blaiog.web

__version__ = "0.0.1b"

#asyncio.AbstractEventLoop.set_debug(enabled=True)

    

def main(config,web=True,trap=True):
    logasync = logging.getLogger("asyncio")
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)s:%(name)s] \
[%(levelname)-5.5s]  %(message)s")

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    logasync.addHandler(consoleHandler)
    
    loop = asyncio.get_event_loop()
   
    def ask_exit(signame="QUIT"):
        """
        http://stackoverflow.com/q/23313720
        """
        log.error("got signal %s: exit" % signame)
        loop.stop()
    
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                ask_exit)
    w = blaiog.web.Web(config,loop)
    asyncio.ensure_future(w.start())
    loop.run_forever()
    loop.close()
    

