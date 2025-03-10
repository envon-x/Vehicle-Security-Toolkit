#!/usr/bin/python3

import sys
import pyfiglet
import argparse
from pathlib import Path

sys.path.append('..')
from utils import shell_cmd, Color


def analysis(src_path: Path):
    mobsf_file = src_path.joinpath('SecScan/mobsf.json')

    cmd = f'docker run --rm -v {src_path}:/src opensecurity/mobsfscan --json -o /src/SecScan/mobsf.json /src'
    output, ret_code = shell_cmd(cmd)

    if mobsf_file.exists():
        return 0
    else:
        with open(f'{mobsf_file}.error', 'w+') as f:
            f.write(output)
        return 1


def argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='A config file containing source code path', type=str, required=True)
    return parser.parse_args()


if __name__ == '__main__':
    print(pyfiglet.figlet_format('src_mobsf'))
    src_dirs = open(argument().config, 'r').read().splitlines()

    for src in src_dirs:
        Color.print_focus(f'[+] [mobsf] {src}')
        src_path = Path(src)

        report_path = src_path.joinpath('SecScan')
        report_path.mkdir(parents=True, exist_ok=True)

        ret = analysis(src_path)
        if ret:
            Color.print_failed('[-] [mobsf] failed')
        else:
            Color.print_success('[+] [mobsf] success')
