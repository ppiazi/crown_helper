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
        self.strategy_list = ['-dfs', '-cfg', '-hybrid', '-random']

    """
    crown을 실행하기 위해 search strategy 별로 임시 workspace를 생성한다.
    """
    def init_workspace(self, dir, cmd, iteration):
        print("Copying directories...")
        for st in self.strategy_list:
            ts = time.time()
            new_folder = dir + st + "-" + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')
            print("\tCopying %s" % new_folder)
            shutil.copytree(target, new_folder)
            self.workspace_list[st] = new_folder
    """
    주어진 command, iteration, search strategy를 기반으로 subprocess를 실행한다.
    CWD(Current Working Directory)는 init_workspace 에서 생성된 값을 사용한다.
    """
    def run_crown(self, cmd, iteration, strategy):
        cwd_str = self.workspace_list[strategy]
        cmd_str = "Starting %s %d %s at %s" % (cmd, iteration, strategy, cwd_str)
        print(cmd_str)
        output_file = open(cmd + strategy + ".result.txt", "wb")
        proc = subprocess.Popen(['run_crown', cmd, str(iteration), strategy], stdout=output_file, stderr=output_file, cwd=cwd_str)
        self.proc_list[strategy] = (proc, cmd_str)
        self.file_list[strategy] = output_file

    """
    search strategy 별로 수행 process를 생성하여 병렬로 진행한다.
    subprocess 들의 작업이 종료될때까지 기다린다.
    """
    def start(self, cmd, iteration):
        for st in self.strategy_list:
            self.run_crown(cmd, iter, st)
        
        run_flag = {}
        for k in self.strategy_list:
            run_flag[k] = True

        while True:
            for proc_st in self.proc_list.keys():
                proc_handle = self.proc_list[proc_st][0]
                proc_cmd_str = self.proc_list[proc_st][1]
                if run_flag[proc_st] == True and proc_handle.poll() != None:
                    print("Finished %s" % (proc_cmd_str))
                    self.file_list[proc_st].flush()
                    self.file_list[proc_st].close()
                    run_flag[proc_st] = False

            exit_flag = True
            for k in run_flag.keys():
                if run_flag[k] == True:
                    exit_flag = False
            if exit_flag == True:
                break

            time.sleep(1)

if __name__ == "__main__":
    target = sys.argv[1]
    cmd = sys.argv[2]
    iter = int(sys.argv[3])

    ceh = CrownExeHelper()

    ceh.init_workspace(target, cmd, iter)
    ceh.start(cmd, iter)
