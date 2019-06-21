import datetime, optparse, re, sys
import twisted
from twisted.internet import defer
from twisted.internet.protocol import Protocol, ClientFactory

# Don't worry about this function, it does some stuff to get some args
def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...

    Welcome to the MadLibs client.
    Run it like this:

        python madlib_client.py <port> ...

    There needs to be a madlib server running on that port.
    """

    parser = optparse.OptionParser(usage)

    _, addresses = parser.parse_args()

    if not addresses:
        print(parser.format_help())
        parser.exit()

    def parse_address(addr):
        if ':' not in addr:
            host = '127.0.0.1'
            port = addr
        else:
            host, port = addr.split(':', 1)

        if not port.isdigit():
            parser.error('Port must be integer.')

        return host, int(port)

    return map(parse_address, addresses)


# HERE'S WHERE IT GETS TWISTY!

#class MadLibProtocol(Protocol):
    # This is where we will overload Protocol callbacks!

class MadlibClientFactory(ClientFactory):
    protocol = Protocol
    # This is where we will spawn protocols (and clean things up when they finish!)
    def __init__(self, deferred):
        self.deferred = deferred


def get_madlib(host, port):
    """
    Ingest madlibs from the given host/port and invoke

        callback(madlib)

    when complete. If there is a failure, invoke:

        errback(err)

    instead, where err is a twisted.python.failure.Failure instance.
    """
    d = defer.Deferred()
    from twisted.internet import reactor
    factory = MadlibClientFactory(d)
    reactor.connectTCP(host, port, factory)
    return d


def madlib_main():
    addresses = parse_args()

    from twisted.internet import reactor

    madlibs = []
    errors = []

    def got_madlib(madlib):
        madlibs.append(madlib)
        print(madlib)
        madlib_done()

    def madlib_failed(err):
        print "Madlib failed:", err
        errors.append(err)
        reactor.stop()

    def madlib_done(_):
        if len(madlibs) + len(errors) == len(addresses):
            reactor.stop()

    for address in addresses:
        host, port = address
        d = get_madlib(host, port)
        d.addCallbacks(got_madlib, madlib_failed)
        d.addBoth(madlib_done)

    reactor.run()

    


if __name__ == '__main__':
    madlib_main()
