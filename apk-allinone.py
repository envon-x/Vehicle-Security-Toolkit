#!/usr/bin/python3

import time
import pyfiglet
import argparse
from pathlib import Path
from collections import defaultdict

from utils import Color
from apk_scan.apk_decompile import apktool, jadx
from apk_scan.apk_androbugs import analysis as androbugs
from apk_scan.apk_audit import init_audit
from apk_scan.apk_cryptoguard import analysis as cryptoguard
from apk_scan.apk_exodus import analysis as exodus
from apk_scan.apk_exodus import get_trackers
from apk_scan.apk_id import analysis as apkid
from apk_scan.apk_jni import analysis as jni
from apk_scan.apk_leaks import analysis as leaks
from apk_scan.apk_mariana import analysis as mariana
from apk_scan.apk_mobsf import analysis as mobsf
from apk_scan.apk_qark import analysis as qark
from apk_scan.apk_quark import analysis as quark
from apk_scan.apk_scanner import analysis as scanner
from apk_scan.apk_speck import analysis as speck
from apk_scan.apk_keyfinder import analysis as keyfinder

# 配置项
mobsf_key = ''


def argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='A config file containing APK path', type=str, required=True)
    parser.add_argument('--decompile', help='Decompile the APK before analysis', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    print(pyfiglet.figlet_format('apk-allinone'))
    args = argument()
    tools_path = Path(__file__).absolute().parent.joinpath('tools')

    plugin = {
        # 必选插件
        'decompile': defaultdict(list),

        # 可选插件
        'androbugs': defaultdict(list),
        'audit': defaultdict(list),
        'cryptoguard': defaultdict(list),
        'exodus': defaultdict(list),
        'apkid': defaultdict(list),
        'jni': defaultdict(list),
        'leaks': defaultdict(list),
        'mariana': defaultdict(list),
        'mobsf': defaultdict(list),
        'qark': defaultdict(list),
        'quark': defaultdict(list),
        'scanner': defaultdict(list),
        'speck': defaultdict(list),
        'keyfinder': defaultdict(list)
    }
    apk_dirs = open(args.config, 'r').read().splitlines()

    # 缓存
    signature = ''
    compiled_signature = ''

    for apk in apk_dirs:
        Color.print_focus(f'[+] {apk}')

        apk_path = Path(apk)
        report_path = apk_path.parent.joinpath('SecScan')
        report_path.mkdir(parents=True, exist_ok=True)

        # apk_decompile
        if args.decompile:
            print('[+] Decompiling ...')
            ret1 = apktool(apk_path, tools_path)
            ret2 = jadx(apk_path, tools_path)
            if ret1 or ret2:
                plugin['decompile']['failed'].append(apk)
                Color.print_failed('[-] [decompile] failed')
            else:
                plugin['decompile']['success'].append(apk)
                Color.print_success('[+] [decompile] success')

        # apk_androbugs
        if 'androbugs' in plugin:
            if ret := androbugs(apk_path):
                plugin['androbugs']['failed'].append(apk)
                Color.print_failed('[-] [androbugs] failed')
            else:
                plugin['androbugs']['success'].append(apk)
                Color.print_success('[+] [androbugs] success')

        # apk_audit
        if 'audit' in plugin:
            audit, app_id = init_audit()
            success_list, error_list = audit.scan_list()
            if apk in success_list:
                plugin['audit']['success'].append(apk)
                Color.print_success('[+] [audit] success')
            elif apk in error_list:
                plugin['audit']['failed'].append(apk)
                Color.print_failed('[-] [audit] failed')
            else:
                scan_id = audit.scan_create(apk_path, app_id)['id']
                while True:
                    r = audit.scan_read(scan_id)
                    if r['status'] == 'Finished':
                        plugin['audit']['success'].append(apk)
                        Color.print_success('[+] [audit] success')
                        break
                    elif r['status'] == 'Error':
                        plugin['audit']['failed'].append(apk)
                        Color.print_failed('[-] [audit] failed')
                        break
                    else:
                        time.sleep(5)

        # apk_cryptoguard
        if 'cryptoguard' in plugin:
            if ret := cryptoguard(apk_path):
                plugin['cryptoguard']['failed'].append(apk)
                Color.print_failed('[-] [cryptoguard] failed')
            else:
                plugin['cryptoguard']['success'].append(apk)
                Color.print_success('[+] [cryptoguard] success')

        # apk_exodus
        if 'exodus' in plugin:
            if not signature or not compiled_signature:
                signature, compiled_signature = get_trackers()
            exodus(apk_path, signature, compiled_signature)
            plugin['exodus']['success'].append(apk)
            Color.print_success('[+] [exodus] success')

        # apk_id
        if 'apkid' in plugin:
            if ret := apkid(apk_path):
                plugin['apkid']['failed'].append(apk)
                Color.print_failed('[-] [apkid] failed')
            else:
                plugin['apkid']['success'].append(apk)
                Color.print_success('[+] [apkid] success')

        # apk_jni
        if 'jni' in plugin:
            if ret := jni(apk_path, tools_path):
                plugin['jni']['failed'].append(apk)
                Color.print_failed('[-] [jni] failed')
            else:
                plugin['jni']['success'].append(apk)
                Color.print_success('[+] [jni] success')

        # apk_leaks
        if 'leaks' in plugin:
            leaks(apk_path)
            plugin['leaks']['success'].append(apk)
            Color.print_success('[+] [leaks] success')

        # apk_mariana
        if 'mariana' in plugin:
            if ret := mariana(apk_path, tools_path):
                plugin['mariana']['failed'].append(apk)
                Color.print_failed('[-] [mariana] failed')
            else:
                plugin['mariana']['success'].append(apk)
                Color.print_success('[+] [mariana] success')

        # apk_mobsf
        if 'mobsf' in plugin:
            if not mobsf_key:
                mobsf_key = input('请输入 mobsf key：')
            if ret := mobsf(mobsf_key, apk_path):
                plugin['mobsf']['failed'].append(apk)
                Color.print_failed('[-] [mobsf] failed')
            else:
                plugin['mobsf']['success'].append(apk)
                Color.print_success('[+] [mobsf] success')

        # apk_qark
        if 'qark' in plugin:
            if ret := qark(apk_path, tools_path):
                plugin['qark']['failed'].append(apk)
                Color.print_failed('[-] [qark] failed')
            else:
                plugin['qark']['success'].append(apk)
                Color.print_success('[+] [qark] success')

        # apk_quark
        if 'quark' in plugin:
            quark(apk_path)
            plugin['quark']['success'].append(apk)
            Color.print_success('[+] [quark] success')

        # apk_scanner
        if 'scanner' in plugin:
            if ret := scanner(apk_path, tools_path):
                plugin['scanner']['failed'].append(apk)
                Color.print_failed('[-] [scanner] failed')
            else:
                plugin['scanner']['success'].append(apk)
                Color.print_success('[+] [scanner] success')

        # apk_speck
        if 'speck' in plugin:
            if ret := speck(apk_path, tools_path):
                plugin['speck']['failed'].append(apk)
                Color.print_failed('[-] [speck] failed')
            else:
                plugin['speck']['success'].append(apk)
                Color.print_success('[+] [speck] success')

        # apk_keyfinder
        if 'keyfinder' in plugin:
            if ret := keyfinder(apk_path, tools_path):
                plugin['keyfinder']['failed'].append(apk)
                Color.print_failed('[-] [keyfinder] failed')
            else:
                plugin['keyfinder']['success'].append(apk)
                Color.print_success('[+] [keyfinder] success')

    print(plugin)
