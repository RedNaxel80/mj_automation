import sys
from connector import Connector


def main():
    port = 5000
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    connector = Connector(port)


if __name__ == '__main__':
    main()

