import argparse as argparse
import subprocess
import sys
import threading
import queue
import requests

MAIN_DESCRIPTION = """
Forwards APRS messages from a source UDP connection on localhost to a
specified HTTP webserver.
"""

worker_q_in = queue.Queue()
worker_q_out = queue.Queue()

def make_worker(args):
    uri = f'{args.http_protocol}://{args.http_host}:{args.http_port}{args.http_resource}'
    def worker():
        while True:
            item = worker_q_in.get()
            response = None

            try:
                response = requests.post(f'{uri}', json={
                    'item': item
                })
            except:
                pass

            if response is None or response.status_code != 200:
                worker_q_out.put('FAIL')

            worker_q_in.task_done()
    return worker

def listen(args):
    command = f"""
    nc -l -u -p {args.udp_port} \
    | sox -t raw -esigned-integer -b 16 -r 48000 - -esigned-integer -b 16 -r 22050 -t raw - \
    | multimon-ng --timestamp -t raw -a AFSK1200 -A -
    """

    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        shell=True
    )

    for line in iter(p.stdout.readline, ""):
        if not worker_q_out.empty():
            # TODO: simple failure mechanism implemented here. in future, we will requeue
            # failed requests and break the loop completly if queue size exceeds some theshold
            status = worker_q_out.get_nowait()
            if status == 'FAIL':
                break;
        worker_q_in.put(line.decode(sys.stdout.encoding))

    worker_q_in.join()

def main():
    parser = argparse.ArgumentParser(description=MAIN_DESCRIPTION)
    parser.add_argument('--udp-port', type=int, help='source UDP port (default: 7355)', default=7355)
    parser.add_argument('--http-protocol', type=str, help='destination HTTP protocol (default: http)', default='http')
    parser.add_argument('--http-host', type=str, help='destination HTTP host (default: 127.0.0.1)', default='127.0.0.1')
    parser.add_argument('--http-port', type=int, help='destination HTTP port (default: 5000)', default=5000)
    parser.add_argument('--http-resource', type=str, help='destination HTTP resource path (default: /)', default='/')
    # TODO: add max re-queue size
    args = parser.parse_args()

    threading.Thread(target=make_worker(args), daemon=True).start()
    listen(args)


if __name__ == "__main__":
    main()