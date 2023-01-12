__Author__ = "Aravind Prabhakar"
# Version: 1.0
# Date: 2023-01-10
# Description: In the event of link down set admin down and login to peer device to enable link up

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.factory.factory_loader import FactoryLoader
from jnpr.junos.exception import ConnectAuthError, ConnectRefusedError,ConnectError, ConnectTimeoutError, RpcError, \
    CommitError
from lxml import etree
from pprint import pprint

import yaml
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("-peer", action='store', dest='PEERIP', help='peer IP')
parser.add_argument("-peerintf", action='store', dest='PEERINTF', help='peer interface name')
parser.add_argument("-lclintf", action='store', dest='LCLINTF', help='local interface name to manage')
args = parser.parse_args()

USER = "root"
PASSWD = "juniper123"
LOCALHOST = "192.167.1.3"
PEERHOST = args.PEERIP

print(args.LCLINTF)
print(args.PEERINTF)

# Device opening
def main():
    dev = Device(host=LOCALHOST,user=USER,passwd=PASSWD)
    dev.open()
    with Config(dev) as cu:
        cu.load("set interfaces {} disable".format(args.LCLINTF), format='set', merge=True)
        cu.commit()
    dev.close()

    pdev = Device(host=PEERHOST, user=USER, passwd=PASSWD)
    pdev.open()
    with Config(pdev) as cu:
        cu.load("delete interfaces {} disable".format(args.PEERINTF), format='set', merge=True)
        cu.commit()
    pdev.close()


if __name__ == "__main__":
    main()
