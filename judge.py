#!/bin/python3

import printer

import json
import re
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor

import requests


class Conf:
    LOCK = threading.Lock()

    CONF_PATH = "./easy-judge-conf.json"

    API_URL = "http://api.paiza.io"
    CREATE_PATH = "/runners/create"
    GET_STATUS_PATH = "/runners/get_status"
    GET_DETAILS_PATH = "/runners/get_details"
    API_KEY = "guest"

    USR_NAME_PATTERN = ".+/(.+)"
    Q_NAME_PATTERN = "(.+)\.(.*)"
    USR_NAME_MATCHER = re.compile(USR_NAME_PATTERN)
    Q_NAME_MATCHER = re.compile(Q_NAME_PATTERN)
    SUCCESS_SYMBOL, FAIL_SYMBOL = "O", "X"

    STATUS_MSG = {
        "waiting": "WAITING",
        "working": "WORKING",
        "done": "DONE",
        "error": "ERROR"
    }
    MAX_LEN_STATUS_MSG = max(map(len, STATUS_MSG.values()))
    STATUS_MSG_PATTERN = "< {status:^{max_len}} > {usr_name} [{working:02d}/{schedule:02d}]"
    ALL_DONE_MSG = "ALL DONE"
    OUT_FILE = "./grades_book.json"

    def __init__(self):
        with open(Conf.CONF_PATH, mode="r") as f:
            j = json.load(f)

        self.src_dirs = j.get("src_dirs", None)
        self.src_dir = j.get("src_dir", None)
        self.ans_dir = j.get("ans_dir", None)
        self.src_langs = j.get("src_langs", None)

        if self.src_dirs is None and self.src_dir is None or self.ans_dir is None or self.src_langs is None:
            raise Exception("conf error")

        self.single = self.src_dir is not None and self.src_dir != ""


def get_status_view(status, max_len, usr_name, working, schedule):
    return Conf.STATUS_MSG_PATTERN.format(
        status=status,
        max_len=max_len,
        usr_name=usr_name,
        working=working,
        schedule=schedule
    )


def update_view(position, jobs, data):
    with Conf.LOCK:
        printer.up(jobs - position)
        printer.erase()
        printer.fprint(data, end="")
        printer.down(jobs - position)
        printer.beginning()


def judge(src, ans, lang, input_=""):
    def validate_res(res):
        if res.status_code != 200:
            raise Exception("api error")

        res = res.json()
        if res.get("error", "") != "":
            raise Exception(res["error"])

        return res

    req = {
        "source_code": src,
        "language": lang,
        "input": input_,
        "api_key": Conf.API_KEY
    }

    res = validate_res(requests.post(f'{Conf.API_URL}{Conf.CREATE_PATH}', data=req))
    session_id = res["id"]
    exec_status = res["status"]
    while exec_status == "running":
        res = validate_res(requests.get(f'{Conf.API_URL}{Conf.GET_STATUS_PATH}', params={"id": session_id, "api_key": Conf.API_KEY}))
        exec_status = res["status"]
        time.sleep(0.1)

    res = validate_res(requests.get(f'{Conf.API_URL}{Conf.GET_DETAILS_PATH}', params={"id": session_id, "api_key": Conf.API_KEY}))
    if res["stderr"] != "":
        return False

    return res["stdout"].rstrip() == ans.rstrip()


def prescoring(conf):
    usr_name = Conf.USR_NAME_MATCHER.search(conf.src_dir).group(1)

    q_info = []
    for q in sorted(os.listdir(conf.src_dir)):
        q_matched = Conf.Q_NAME_MATCHER.search(q)
        if q_matched is None:
            continue

        q_info.append(q_matched)

    printer.fprint(get_status_view(Conf.STATUS_MSG["waiting"], Conf.MAX_LEN_STATUS_MSG, usr_name, 0, len(q_info)))
    return {"usr_name": usr_name, "src_dir": conf.src_dir, "q_info": q_info}


def scoring(conf, position, jobs, usr_name, src_dir, q_info):
    score = {}
    for i, qf in enumerate(q_info):
        q, q_name, prefix = qf.group(0), qf.group(1), qf.group(2)

        with open(f'{src_dir}/{q}', mode="r") as f:
            src = f.read()

        with open(f'{conf.ans_dir}/{q_name}.ans', mode="r") as f:
            ans = f.read()

        update_view(position, jobs, get_status_view(Conf.STATUS_MSG["working"], Conf.MAX_LEN_STATUS_MSG, usr_name, i + 1, len(q_info)))
        score[q_name] = conf.SUCCESS_SYMBOL if judge(src, ans, conf.src_langs[prefix]) else conf.FAIL_SYMBOL

    update_view(position, jobs, get_status_view(Conf.STATUS_MSG["done"], Conf.MAX_LEN_STATUS_MSG, usr_name, i + 1, len(q_info)))
    return usr_name, score


def do_dirs(conf):
    result = {}
    pre = []
    for src_dir in sorted(os.listdir(conf.src_dirs)):
        conf.src_dir = f'{conf.src_dirs}/{src_dir}'
        pre.append(prescoring(conf))

    with ThreadPoolExecutor() as executor:
        futures = [None] * len(pre)
        for i, unit in enumerate(pre):
            futures[i] = executor.submit(scoring, conf, i, len(pre), **unit)

        result = {usr_name: score for usr_name, score in sorted([future.result() for future in futures], key=lambda x: x[0])}

    return result


def do_dir(conf):
    usr_name, score = scoring(conf, 0, 1, **prescoring(conf))

    return {usr_name: score}


def main():
    conf = Conf()
    if conf.single:
        result = do_dir(conf)
    else:
        result = do_dirs(conf)

    with open(conf.OUT_FILE, mode="w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(Conf.ALL_DONE_MSG)


if __name__ == "__main__":
    main()
