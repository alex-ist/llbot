import os
import re


def reversed_lines(file, key:str):
    "Generate the lines of file in reverse order."
    part = ''
    for block in reversed_blocks(file):
        for c in reversed(block):
            if c == '\n' and part:
                line=part[::-1]
                match = re.search(r'.*- (\d+):.*', line)
                if match is None or match.group(1) == key:                
                    yield line
                part = ''
            part += c
    if part: 
        line=part[::-1]
        match = re.search(r'.*"- (\d+):.*', line)
        if match is None or match.group(1) == key:                
            yield line

def reversed_blocks(file, blocksize=4096):
    "Generate blocks of file's contents in reverse order."
    file.seek(0, os.SEEK_END)
    here = file.tell()
    while 0 < here:
        delta = min(blocksize, here)
        here -= delta
        file.seek(here, os.SEEK_SET)
        yield file.read(delta)

from itertools import islice

def get_last_n_lines(path, user_id:int, sz):
    f=open (path,"r")
    lines = list(islice(reversed_lines(f, str(user_id)), sz))
    f.close()
    return lines[::-1]

#r=get_last_n_lines('log/ll.log', 484679683, 4)
#print (r, end="")
