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

PATTERN = "Iteration"

def parse(result_file):
    iter_result = []

    try:
        f = open(result_file, "r", errors='ignore')
    except:
        print("File open error : %s" % result_file)
        return iter_result

    lines = f.readlines()

    for line in lines:
        if PATTERN in line:
            split_item = line.split()
            rst_iter = split_item[1]
            rst_branch = split_item[5]

            iter_result.append((rst_iter, rst_branch))
    
    f.close()
    
    return iter_result
