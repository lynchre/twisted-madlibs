import datetime, optparse, re, sys
import twisted
from twisted.internet import defer
from twisted.internet.protocol import Protocol, ClientFactory

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

class MadLibProtocol(Protocol):
    def dataReceived(self, data):
        wordList = re.sub("[^\w]", " ",  data).split()
        if len(wordList) == 2:
            self.getWord(wordList[0], wordList[1])
        else:
            self.madlib = data

    def getWord(self, index, type):
        article = 'a'
        if type[0] in ['a', 'e', 'i', 'o', 'u']:
            article = 'an'

        s = raw_input('Enter {} {}: '.format(article, type))
        self.transport.write("{} {}".format(index, s))
        
    def connectionLost(self, reason):
        self.madLibComplete(self.madlib)

    def madLibComplete(self, madlib):
        self.factory.madLibFinished(madlib)

class MadlibClientFactory(ClientFactory):

    protocol = MadLibProtocol

    def __init__(self, deferred):
        self.deferred = deferred

    def madLibFinished(self, madlib):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback(madlib)

    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)


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

