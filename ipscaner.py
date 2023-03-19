import argparse
import socket
import subprocess
import sys
import time


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


def scan(host, np, port_range=None, timeout=1, show_processes=False):
    """
    Scans the given host (str) and returns True if the host is online.
    If np flag is set to True, then only checks if host is online and does not scan ports.
    If port_range is given, only scans ports within that range.
    The timeout parameter determines the connection timeout for port scanning.
    If show_processes flag is set to True, shows the list of running processes on the target machine.
    """
    if port_range:
        start_port, end_port = port_range
    else:
        start_port, end_port = 1, 65536

    if not np:
        for port in range(start_port, end_port + 1):
            if scan_port(host, port):
                print(f"Port {port} on {host} is open.")

    if ping(host):
        print(f"{host} is online.")

        if show_processes:
            print("Running processes on the target machine:")
            try:
                cmd = subprocess.Popen(["ssh", host, "ps aux"], stdout=subprocess.PIPE)
                output = cmd.communicate()[0]
                print(output.decode('utf-8'))
            except subprocess.CalledProcessError as e:
                print(f"Failed to retrieve running processes: {e}")

        return True
    else:
        print(f"{host} is offline.")
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan IP addresses and ports.')
    parser.add_argument('ip_address', metavar='ip', type=str, nargs='+', help='IP address(es) to scan')
    parser.add_argument('-np', '--no-port', action='store_true', help='Do not scan ports')
    parser.add_argument('-p', '--port-range', metavar='start:end', type=str, help='Port range to scan (e.g. 1:100)')
    parser.add_argument('-t', '--timeout', metavar='seconds', type=float, default=1, help='Connection timeout for port scanning')
    parser.add_argument('-s', '--show-processes', action='store_true', help='Show running processes on the target machine')

    args = parser.parse_args()

    for ip in args.ip_address:
        port_range = None
        if args.port_range:
            try:
                start, end = map(int, args.port_range.split(':'))
                if start > end:
                    raise ValueError("Invalid port range")
                port_range = (start, end)
            except ValueError:
                print("Invalid port range specified, skipping port scanning.")

        scan(ip, args.no_port, port_range=port_range, timeout=args.timeout, show_processes=args.show_processes)

