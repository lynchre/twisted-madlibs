# This is the twisted madlib server
import optparse, os, re
import twisted
from twisted.internet.protocol import ServerFactory, Protocol


ML_INDEX = [
    '13 noun',
    '20 noun',
    '32 adjective',
    '38 noun',
    '42 noun',
    '46 verb',
    '56 noun',
    '66 noun',
    '95 verb',
    '99 noun',
    '119 verb',
    '131 adjective',
    '152 noun',
    '178 firstname',
    '179 lastname',
]

# Don't worry about this function, it does some stuff to get some args
def parse_args():
    usage = """usage: %prog [options] madlib-file

This is the Madlib Server, Twisted edition.
Run it like this:

  python madlib_server.py <path-to-madlib-file>
"""

    parser = optparse.OptionParser(usage)

    help = "The port to listen on. Default to a random available port."
    parser.add_option('--port', type='int', help=help)

    help = "The interface to listen on. Default is localhost."
    parser.add_option('--iface', help=help, default='localhost')

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error('Provide exactly one madlib file.')

    madlib_file = args[0]

    if not os.path.exists(args[0]):
        parser.error('No such file: %s' % madlib_file)

    return options, madlib_file


# HERE'S WHERE IT GETS TWISTY!

class MadlibProtocol(Protocol):
    def connectionMade(self):
        print("SOMEONE CONNECTED AYY")
    # This is where we will overload Protocol callbacks!


class MadlibFactory(ServerFactory):

    protocol = MadlibProtocol

    # This is where we will spawn protocols from!

    
def main():
    options, madlib_file = parse_args()

    madlib = open(madlib_file).read()

    factory = MadlibFactory(madlib, ML_INDEX)

    from twisted.internet import reactor

    port = reactor.listenTCP(options.port or 0, factory, interface=options.iface)

    print('Serving {} on {}.'.format(madlib_file, port.getHost()))

    reactor.run()


if __name__ == "__main__":
    main()