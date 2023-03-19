import argparse
import socket
import subprocess
import sys
import threading
 

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    """
    if sys.platform.startswith('win'):
        param = '-n'
    else:
        param = '-c'

    completed_process = subprocess.run(['ping', param, '1', host], stdout=subprocess.PIPE)
    return completed_process.returncode == 0


def scan_port(host, port):
    """
    Returns True if the port (int) on host (str) is open.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0


def scan(host, np, ports=None, showprocess=False):
    """
    Scans the given host (str) and returns True if the host is online.
    If np flag is set to True, then only checks if host is online and does not scan ports.
    """
    if showprocess:
        print(f"Scanning {host}...")
    if not np:
        if ports is None:
            ports = range(1, 65536)
        for port in ports:
            if scan_port(host, port):
                print(f"Port {port} on {host} is open.")
                if showprocess:
                    print(f"Service running on port {port}: {socket.getservbyport(port)}")

    if ping(host):
        print(f"{host} is online.")
        return True
    else:
        print(f"{host} is offline.")
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan IP addresses and ports.')
    parser.add_argument('ip_address', metavar='ip', type=str, nargs='+', help='IP address(es) to scan')
    parser.add_argument('-np', '--no-port', action='store_true', help='Do not scan ports')
    parser.add_argument('-p', '--ports', type=str, help='Port number or range of ports to scan, e.g. 22 or 1-65535')
    parser.add_argument('-sp', '--show-process', action='store_true', help='Show scan progress and running services')

    args = parser.parse_args()

    for ip in args.ip_address:
        ports = None
        if args.ports:
            ports_str = args.ports.split('-')
            if len(ports_str) == 1:
                ports = [int(ports_str[0])]
            elif len(ports_str) == 2:
                ports = range(int(ports_str[0]), int(ports_str[1])+1)
        threading.Thread(target=scan, args=(ip, args.no_port, ports, args.show_process)).start()

