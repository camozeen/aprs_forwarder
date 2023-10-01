import argparse as argparse
import subprocess
import sys
import threading
import queue
import requests
import time


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
                response = requests.post(f'{uri}', json=item)
            except:
                pass

            if response is None or response.status_code != 200:
                worker_q_out.put(item)

            worker_q_in.task_done()
    return worker


def listen(args):
    p = subprocess.Popen(
        f"""
        nc -l -u -p {args.udp_port} \
        | sox -t raw -esigned-integer -b 16 -r 48000 - -esigned-integer -b 16 -r 22050 -t raw - \
        | multimon-ng -t raw -a AFSK1200 -A -
        """,
        stdout=subprocess.PIPE,
        shell=True
    )

    for line in iter(p.stdout.readline, ""):
        if not worker_q_out.empty():
            if worker_q_out.qsize() >= args.retry_limit:
                print(f'CRITICAL: failure queue is full. shutting down.')
                break;

            failed_item_count = worker_q_out.qsize()
            if failed_item_count == (args.retry_limit * 0.5):
                print(f'WARNING: failure queue is 50% full - items: {failed_item_count}.')

            failed_item_i = 0
            while failed_item_i < failed_item_count:
                failed_item = worker_q_out.get_nowait()
                worker_q_in.put(failed_item)
                failed_item_i += 1

        worker_q_in.put({
            'data': line.decode(sys.stdout.encoding),
            'ts': time.time()
        })

    worker_q_in.join()


def main():
    parser = argparse.ArgumentParser(description=MAIN_DESCRIPTION)
    parser.add_argument('--udp-port', type=int, help='source UDP port (default: 7355)', default=7355)
    parser.add_argument('--http-protocol', type=str, help='destination HTTP protocol (default: http)', default='http')
    parser.add_argument('--http-host', type=str, help='destination HTTP host (default: 127.0.0.1)', default='127.0.0.1')
    parser.add_argument('--http-port', type=int, help='destination HTTP port (default: 5000)', default=5000)
    parser.add_argument('--http-resource', type=str, help='destination HTTP resource path (default: /)', default='/')
    parser.add_argument('--retry-limit', type=int, help='number of messages to retry before shutdown (default: 50)', default=50)
    args = parser.parse_args()

    print('INFO: starting worker thread')
    print(f'    | destination: {args.http_protocol}://{args.http_host}:{args.http_port}{args.http_resource}')
    threading.Thread(target=make_worker(args), daemon=True).start()
    print('INFO: starting main thread')
    print(f'    | listen UDP: {args.udp_port}')
    listen(args)
    print('INFO: shutting down')


if __name__ == "__main__":
    main()
