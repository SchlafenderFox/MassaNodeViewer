import logging
import re
import subprocess

import requests
from requests.exceptions import Timeout, ConnectionError

from app.db import DB


def get_prometheus_info(name, url):
    try:
        response = requests.get(url=url)
        return response.text
    except (Timeout, ConnectionError):
        logging.error(f"[{name}] Timeout connection")
        return None


def get_cycles_info(cycles: str):
    parsed_cycles = list()

    for cycle in cycles.split('\n'):
        info = dict()
        try:
            info['produce_blocks'] = int(re.search(r'(?<=produced )[0-9]+', cycle).group(0))
            info['failed_blocks'] = int(re.search(r'(?<=failed )[0-9]+', cycle).group(0))
            info['cycles_id'] = int(re.search(r'(?<=cycle )[0-9]+', cycle).group(0))
        except:
            continue

        parsed_cycles.append(info)

    db = DB()
    db.insert_new_cycles(parsed_cycles)

    stored_cycles = db.get_all_cycles()

    active_cycles = len(stored_cycles)

    produce_blocks = 0
    failed_blocks = 0
    for cycle in stored_cycles:
        produce_blocks += cycle['produce_blocks']
        failed_blocks += cycle['failed_blocks']

    return active_cycles, produce_blocks, failed_blocks


def get_additional_info():
    output = subprocess.check_output(['bash', './get_node_info.sh']).decode('utf-8')

    node_info, cycles_info = output.split('Cycles:')

    node_info_lines = node_info.split('\n')
    address = node_info_lines[0].split(':')[-1]
    final_balance = node_info_lines[1].split(':')[-1]
    candidate_balance = node_info_lines[2].split(':')[-1]
    locked_balance = node_info_lines[3].split(':')[-1]
    active_rolls = node_info_lines[4].split(':')[-1]
    final_rolls = node_info_lines[5].split(':')[-1]
    candidate_rolls = node_info_lines[6].split(':')[-1]

    additional = "{" + f'address="{address}"' + "}"

    info = f"# HELP final_balance\n" \
           f"# TYPE final_balance gauge\n" \
           f"final_balance{additional} {final_balance}\n" \
           f"# HELP candidate_balance\n" \
           f"# TYPE candidate_balance gauge\n" \
           f"candidate_balance{additional} {candidate_balance}\n" \
           f"# HELP locked_balance\n" \
           f"# TYPE locked_balance gauge\n" \
           f"locked_balance{additional} {locked_balance}\n" \
           f"# HELP active_rolls\n" \
           f"# TYPE active_rolls gauge\n" \
           f"active_rolls{additional} {active_rolls}\n" \
           f"# HELP final_rolls\n" \
           f"# TYPE final_rolls gauge\n" \
           f"final_rolls{additional} {final_rolls}\n" \
           f"# HELP candidate_rolls\n" \
           f"# TYPE candidate_rolls gauge\n" \
           f"candidate_rolls{additional} {candidate_rolls}\n"

    active_cycles, produce_blocks, failed_blocks = get_cycles_info(cycles_info)

    if active_cycles is None or produce_blocks is None or failed_blocks is None:
        return info

    info = info + f"# HELP active_cycles\n" \
                  f"# TYPE active_cycles gauge\n" \
                  f"active_cycles{additional} {active_cycles}\n" \
                  f"# HELP produce_blocks\n" \
                  f"# TYPE produce_blocks gauge\n" \
                  f"produce_blocks{additional} {produce_blocks}\n" \
                  f"# HELP failed_blocks\n" \
                  f"# TYPE failed_blocks gauge\n" \
                  f"failed_blocks{additional} {failed_blocks}\n"

    return info
