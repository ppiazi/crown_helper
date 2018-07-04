# -*- coding: utf-8 -*-
"""
Copyright 2018 Joohyun Lee(ppiazi@gmail.com)
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import subprocess
import os
import sys
import time
import datetime
import shutil
import getopt
import crown_result_parser
import xlsxwriter

__author__ = "ppiazi"
__version__ = "v0.0.1"

class CrownExeHelper:
    """
    내부변수들을 초기화한다.
    - self.proc_list : search strategy 별로 subprocess handle과 실행명령 문자열을 보관함.
    - self.workspace_list : search strategy 별로 임시 workspace 정보를 저장함.
    - self.file_list : search strategy 별로 stdout / stderr 정보를 저장하는 파일 객체를 저장함.
    - self.strategy_list : search strategy 종류를 저장함.
    """
    def __init__(self):
        self.proc_list = {}
        self.workspace_list = {}
        self.file_list = {}
        self.file_name_list = {}
        self.strategy_list = ['-dfs', '-cfg', '-hybrid', '-random']

    """
    crown을 실행하기 위해 search strategy 별로 임시 workspace를 생성한다.
    """
    def init_workspace(self, target_dir, cmd, iteration):
        print("Copying directories...")
        for st in self.strategy_list:
            ts = time.time()
            new_folder = target_dir + st + "-" + str(iteration) + "-" + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')
            print("\tCopying %s" % new_folder)
            shutil.copytree(target_dir, new_folder)
            self.workspace_list[st] = new_folder
    """
    주어진 command, iteration, search strategy를 기반으로 subprocess를 실행한다.
    CWD(Current Working Directory)는 init_workspace 에서 생성된 값을 사용한다.
    """
    def run_crown(self, cmd, iteration, strategy):
        cwd_str = self.workspace_list[strategy]
        cmd_str = "%s %d %s at %s" % (cmd, iteration, strategy, cwd_str)
        print("\tStarting " + cmd_str)

        stdout_result_file_name = cmd + strategy + ".stdout.result.txt"
        stderr_result_file_name = cmd + strategy + ".stderr.result.txt"
        stdoutput_file = open(stdout_result_file_name, "wb")
        stderr_file = open(stderr_result_file_name, "wb")
        self.file_name_list[strategy] = stdout_result_file_name
        self.file_list[strategy] = (stdoutput_file, stderr_file)
        
        proc = subprocess.Popen(['run_crown', cmd, str(iteration), strategy], stdout=stdoutput_file, stderr=stderr_file, cwd=cwd_str)
        self.proc_list[strategy] = (proc, cmd_str)        

    """
    search strategy 별로 수행 process를 생성하여 병렬로 진행한다.
    subprocess 들의 작업이 종료될때까지 기다린다.
    """
    def start(self, cmd, iteration):
        print("Starting run_crown...")
        for st in self.strategy_list:
            self.run_crown(cmd, iteration, st)
        
        run_flag = {}
        for k in self.strategy_list:
            run_flag[k] = True

        while True:
            for proc_st in self.proc_list.keys():
                proc_handle = self.proc_list[proc_st][0]
                proc_cmd_str = self.proc_list[proc_st][1]
                if run_flag[proc_st] == True and proc_handle.poll() != None:
                    print("\tFinished %s" % (proc_cmd_str))
                    self.file_list[proc_st][0].flush()
                    self.file_list[proc_st][0].close()
                    self.file_list[proc_st][1].flush()
                    self.file_list[proc_st][1].close()
                    run_flag[proc_st] = False

            exit_flag = True
            for k in run_flag.keys():
                if run_flag[k] == True:
                    exit_flag = False
            if exit_flag == True:
                break

            time.sleep(1)
    
    """
    run_crown의 결과 파일을 읽어 내부 데이터로 변환한다.
    """
    def gather_result(self):
        print("Gathering results...")
        result_per_ss = {}

        for st in self.file_name_list.keys():
            result_file_name = self.file_name_list[st]
            print("\tParsing %s" % result_file_name)
            tmp_list = crown_result_parser.parse(result_file_name)
            result_per_ss[st] = tmp_list

        return result_per_ss

    """
    run_crown의 결과 파일을 읽어 내부 데이터를 엑셀 파일로 저장한다.
    """    
    def save_result(self, output_file):
        wbk = xlsxwriter.Workbook(output_file)
        sheet = wbk.add_worksheet("result")

        rst = self.gather_result()

        sheet.write(0, 0, "Iteration")
        i = 1
        max_iter = 0
        for st in rst.keys():
            sheet.write(0, i, st)
            i = i + 1
            if len(rst[st]) > max_iter:
                max_iter = len(rst[st])

        for i in range(0, max_iter):
            row = i + 1
            sheet.write(row, 0, i + 1)

            col = 1
            for st in rst.keys():
                try:
                    sheet.write(row, col, rst[st][i][1])
                except:
                    sheet.write(row, col, "NA")
                col = col + 1

        wbk.close()

"""
사용법에 대한 내용을 콘솔에 출력한다.
"""
def print_usage():
    print("FilesInfoReader.py [-f <folder>] [-c <executable command>] [-i <iteration count>]")
    print("    Author %s" % __author__)
    print("    Version %s" % __version__)

if __name__ == "__main__":
    p_target = None
    p_cmd = None
    p_iter = 100

    optlist, args = getopt.getopt(sys.argv[1:], "f:c:i:")

    for op, p in optlist:
        if op == "-f":
            p_target = p
        elif op == "-c":
            p_cmd = p
        elif op == "-i":
            try:
                tmp_int = int(p)
                p_iter = tmp_int
            except:
                print("Invalid iteration count : %s" % p)
        else:
            print("Invalid argument : " % (op, p))
    
    if p_target == None or p_cmd == None:
        print_usage()
        os._exit(1)

    ceh = CrownExeHelper()

    ceh.init_workspace(p_target, p_cmd, p_iter)
    ceh.start(p_cmd, p_iter)
    ceh.save_result("result.xlsx")
