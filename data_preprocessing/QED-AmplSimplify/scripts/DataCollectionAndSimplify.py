"""
COMPLETELY UNFINISHED

Run this script from base folder like `python scripts/DataCollectionAndSimplify.py`.
Read in amplitudes and squared amplitudes the way they were exported from MARTY.
Then we simplify the squared amplitudes with SYMPY.
A timeout is added. This is because somehow if SYMPY has an unlucky random seed for a
simplify, it will not finish.

    - `ampl_folders_prefix = "../../data-generation-marty/QED/out/ampl/"`
        This is the folder prefix for the amplitudes. The actual folder will have e.g. `1to2/` appended to this.
    - `sqampl_raw_folders_prefix = "../../data-generation-marty/QED/out/sq_ampl_raw/"`
        This is the folder prefix for the squared amplitudes. The actual folder will have e.g. `1to2/` appended to this.
    - `process_multiplicities = ["1to2/", "2to1/", "2to2/", "2to3/", "3to2/"]`
        Folders in the `ampl_folders_prefix` and `sqampl_raw_folders_prefix folders`.
    - `export_folder = "../../data.nosync/"`
        Where the amplitudes and squared amplitudes get exported. They will be named like `QED_amplitudes_TreeLevel_1to2.txt` 
        and `QED_sqamplitudes_TreeLevel_simplified_1to2.txt`
    - `n_cpus = 10`
        Number of CPUs to use in parallel
    - `fresh_start= False`
        False to continue previous calculation where left off.

The squared amplitudes are:
    - simplified using `sympy.factor`
    - shortened where some tokens are combined and e.g. i-->I^2
    - simplified again so that things like I^2=-1 get fixed.
"""


import sys
import os
from icecream import ic 
import sympy as sp
from tqdm import tqdm
import csv
import numpy as np
from datetime import datetime
from math import ceil
import multiprocessing as mp
import multiprocessing.queues as mpq
import functools
import dill
from typing import Tuple, Callable, Dict, Optional, Iterable

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from source.helpers import process_ampl_sqampl, shorten_expression_helper


def read_amplitudes_and_raw_squares(folder_ampl, folder_sqampl_raw):
    """
    Read amplitudes in prefix format, but squared amplitudes in raw marty format.
    This is good, becaues the squared amplitudes can be read by sympy and simplified.
    """
    files_ampl = os.listdir(folder_ampl) 
    files_sqampl = os.listdir(folder_sqampl_raw) 
    assert len(files_ampl) == len(files_sqampl)
    # to check if order of files is correct
    skip = len("ampl")
    files_sqampl_generated = ["sq_ampl_raw"+f[skip:] for f in files_ampl]
    assert files_sqampl == files_sqampl_generated

    ampls = []
    sqampls = []
    for file in files_ampl:
        with open(folder_ampl+file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                ampls.append(row[:-1])

    for file in files_sqampl:
        with open(folder_sqampl_raw+file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                sqampls.append(row[0])

    return (ampls, sqampls)


class TimeoutError(Exception):

    def __init__(self, func, timeout):
        self.t = timeout
        self.fname = func.__name__

    def __str__(self):
            return f"function '{self.fname}' timed out after {self.t}s"


def _lemmiwinks(func: Callable, args: Tuple[object], kwargs: Dict[str, object], q: mp.Queue):
    """lemmiwinks crawls into the unknown"""
    q.put(dill.loads(func)(*args, **kwargs))


def killer_call(func: Callable = None, timeout: int = 10*60) -> Callable:
    """
    Single function call with a timeout

    Args:
        func: the function
        timeout: The timeout in seconds
    """

    if not isinstance(timeout, int):
        raise ValueError(f'timeout needs to be an int. Got: {timeout}')

    if func is None:
        return functools.partial(killer_call, timeout=timeout)

    @functools.wraps(killer_call)
    def _inners(*args, **kwargs) -> object:
        q_worker = mp.Queue()
        proc = mp.Process(target=_lemmiwinks, args=(dill.dumps(func), args, kwargs, q_worker))
        proc.start()
        try:
            return q_worker.get(timeout=timeout)
        except mpq.Empty:
            raise TimeoutError(func, timeout)
        finally:
            try:
                proc.terminate()
            except:
                ic("tried proc.terminate() for process that took too long, but failed")
                pass
    return _inners


def _queue_mgr(func_str: str, q_in: mp.Queue, q_out: mp.Queue, timeout: int, pid: int, timeout_logfile: str) -> object:
    """
    Controls the main workflow of cancelling the function calls that take too long
    in the parallel map

    Args:
        func_str: The function, converted into a string via dill (more stable than pickle)
        q_in: The input queue
        q_out: The output queue
        timeout: The timeout in seconds
        pid: process id
    """
    while not q_in.empty():
        positioning, x  = q_in.get()
        q_worker = mp.Queue()
        proc = mp.Process(target=_lemmiwinks, args=(func_str, (x,), {}, q_worker,))
        proc.start()
        try:
            # print(f'[{pid}]: {positioning}: getting')
            res = q_worker.get(timeout=timeout)
            # print(f'[{pid}]: {positioning}: got')
            q_out.put((positioning, res))
        except mpq.Empty:
            q_out.put((positioning, x))
            # print(f'[{pid}]: {positioning}: timed out ({timeout}s)')
            # with open(timeout_logfile, "a") as f:
            #     f.write("Timed out after "+str(timeout)+" seconds. Argument:" + x + "\n")
        finally:
            try:
                proc.terminate()
                # print(f'[{pid}]: {positioning}: terminated')
            except:
                pass
    # print(f'[{pid}]: completed!')


def killer_pmap(func: Callable, iterable: Iterable, cpus: Optional[int] = None, timeout: int = 10*60,
        timeout_logfile = "log/timeout_log.log"):
    """
    Parallelisation of func across the iterable with a timeout at each evaluation

    Args:
        func: The function
        iterable: The iterable to map func over
        cpus: The number of cpus to use. Default is the use max - 2.
        timeout: kills the func calls if they take longer than this in seconds
    """

    if cpus is None:
        cpus = max(mp.cpu_count() - 2, 1)
        if cpus == 1:
            raise ValueError('Not enough CPUs to parallelise. You only have 1 CPU!')
        else:
            print(f'Optimising for {cpus} processors')

    q_in = mp.Queue()
    q_out = mp.Queue()
    sent = [q_in.put((i, x)) for i, x in enumerate(iterable)]

    processes = [
        mp.Process(target=_queue_mgr, args=(dill.dumps(func), q_in, q_out, timeout, pid, timeout_logfile))
        for pid in range(cpus)
    ]
    # print(f'Started {len(processes)} processes')
    for proc in processes:
        proc.start()

    result = [q_out.get() for _ in sent]

    for proc in processes:
        proc.terminate()

    return [x for _, x, in sorted(result)]


def delete_out_files(outfile_amplitudes, outfile_sqamplitudes_simplified, progress_file):
    """Try to delete files and print if done so."""
    print("Starting fresh. Deleting "+progress_file)
    if os.path.exists(progress_file):
        os.remove(progress_file)
    if os.path.exists(outfile_amplitudes):
        print("Deleting "+outfile_amplitudes)
        os.remove(outfile_amplitudes)
    if os.path.exists(outfile_sqamplitudes_simplified):
        print("Deleting "+outfile_sqamplitudes_simplified)
        os.remove(outfile_sqamplitudes_simplified)


def process_in_batches_(amplitudes, squared_amplitudes, name, batch_start,   # delete files and start fresh
                       batch_size=100,
                       export_folder="../../data.nosync/",
                       log_folder="log/",
                       n_cpus=10,
                       timeout=4*60,
                       ):
    """
    Simplify amplitudes with SYMPY.
    - in batches
    - parallelized
    - with timeout
    """
    print("Processing", name, "processes.")
    assert len(amplitudes) == len(squared_amplitudes)

    number_of_batches = ceil(len(amplitudes) / batch_size)
    outfile_amplitudes = export_folder + "QED_amplitudes_TreeLevel_" + name[:-1] + ".txt"
    outfile_sqamplitudes_simplified = export_folder + "QED_sqamplitudes_TreeLevel_simplified_" + name[:-1] + ".txt"
    progress_file = log_folder + "progress_" + name[:-1] + ".log"
    f_ampl = open(outfile_amplitudes, "a")
    f_sqampl = open(outfile_sqamplitudes_simplified, "a")
    for i_batch in tqdm(range(batch_start, number_of_batches)):
        ampl_batch = amplitudes[i_batch*batch_size:(i_batch+1)*batch_size]
        sqampl_batch = squared_amplitudes[i_batch*batch_size:(i_batch+1)*batch_size]
        # ampl_sqampl_simplified = list(map(process_ampl_sqampl, zip(ampl_batch, sqampl_batch)))
        # ampl_sqampl = list(killer_pmap(shorten_expression_helper, zip(ampl_batch, sqampl_batch),
        #                                           cpus=n_cpus, timeout=timeout))
        ampl_sqampl = list(killer_pmap(process_ampl_sqampl, zip(ampl_batch, sqampl_batch),
                                                  cpus=n_cpus, timeout=timeout))
        ampl_sqampl = list(killer_pmap(shorten_expression_helper, ampl_sqampl,
                                                  cpus=n_cpus, timeout=timeout))
        ampl_sqampl = list(killer_pmap(process_ampl_sqampl, ampl_sqampl,
                                                  cpus=n_cpus, timeout=timeout))
        ampl_sqampl = list(killer_pmap(shorten_expression_helper, ampl_sqampl,
                                                  cpus=n_cpus, timeout=timeout))

        ampl_batch_2 = [a for a, _ in ampl_sqampl]
        sqampl_simplified = [sqa for _, sqa in ampl_sqampl]
        out_amplitudes_str = [";".join(x) for x in ampl_batch_2]
        out_sqamplitudes_simplified_str = [str(x) for x in sqampl_simplified]

        with open(progress_file, "a") as f_prog:
            f_prog.write("batch: "+str(i_batch)+"\n")
        f_ampl.write("\n".join(out_amplitudes_str)+"\n")
        f_sqampl.write("\n".join(out_sqamplitudes_simplified_str)+"\n")

    f_ampl.close()
    f_sqampl.close()


def process_in_batches(amplitudes_folder_prefix, squared_amplitudes_folder_prefix, name, 
                       batch_size=100,
                       fresh_start=True,   # delete files and start fresh
                       export_folder="../../data.nosync/",
                       log_folder="log/",
                       n_cpus=10,
                       timeout=4*60,
                       ):

    progress_file = log_folder + "progress_" + name[:-1] + ".log"
    outfile_amplitudes = export_folder + "QED_amplitudes_TreeLevel_" + name[:-1] + ".txt"
    outfile_sqamplitudes_simplified = export_folder + "QED_sqamplitudes_TreeLevel_simplified" + name[:-1] + ".txt"
    amplitudes_folder = amplitudes_folder_prefix + process_mult
    sqamplitudes_folder = squared_amplitudes_folder_prefix + process_mult
    data_already_loaded = False
    ic(fresh_start)
    if fresh_start:
        batch_start = 0
        delete_out_files(outfile_amplitudes, outfile_sqamplitudes_simplified, progress_file)

        print("Reading", process_mult, "processes.")
        amplitudes, squared_amplitudes = read_amplitudes_and_raw_squares(amplitudes_folder, sqamplitudes_folder)
        data_already_loaded = True
        number_of_batches = ceil(len(amplitudes) / batch_size)
        with open(progress_file, "w") as f_prog:
            f_prog.write("Starting processing of " + name + "processes.\n")
            f_prog.write("lines:"+str(len(amplitudes))+"\n")
            f_prog.write("batch_size:"+str(batch_size)+"\n")
            f_prog.write("batches: "+str(number_of_batches)+"\n")
            f_prog.write("------------------------\n")
    else:
        print("Resuming calulation. Reading progress file", progress_file)
        try:
            with open(progress_file) as f_prog:
                progress_file_contents = [line for line in f_prog.readlines()]
                batch_start = int(progress_file_contents[-1][7:]) + 1
            print("Resuming from batch", batch_start)
            total_batches = int(progress_file_contents[3][8:])
            print("Total batches:", total_batches)
            if batch_start == total_batches:
                print("Already finished, nothing to do. Skipping.")
                return 0
        except:
            print("Didn't find progress file", progress_file, ". Starting from batch 0.")
            batch_start = 0
            amplitudes, squared_amplitudes = read_amplitudes_and_raw_squares(amplitudes_folder, sqamplitudes_folder)
            number_of_batches = ceil(len(amplitudes) / batch_size)
            data_already_loaded = True
            with open(progress_file, "w") as f_prog:
                f_prog.write("Starting processing of " + name + "processes.\n")
                f_prog.write("lines:"+str(len(amplitudes))+"\n")
                f_prog.write("batch_size:"+str(batch_size)+"\n")
                f_prog.write("batches: "+str(number_of_batches)+"\n")
                f_prog.write("------------------------\n")

    print("Reading", process_mult, "processes.")

    if not data_already_loaded:
        amplitudes, squared_amplitudes = read_amplitudes_and_raw_squares(amplitudes_folder, sqamplitudes_folder)
    process_in_batches_(amplitudes, squared_amplitudes, name=process_mult, batch_size=batch_size, batch_start=batch_start,
                       export_folder=export_folder, n_cpus=n_cpus, timeout=timeout, log_folder=log_folder)

if __name__=="__main__":
    ampl_folders_prefix = "../../data-generation-marty/QED/out/ampl/"
    sqampl_raw_folders_prefix = "../../data-generation-marty/QED/out/sq_ampl_raw/"
    process_multiplicities = ["1to2/", "2to1/", "2to2/", "2to3/", "3to2/"]
    export_folder = "../../data.nosync/"   # where the amplitudes and squared amplitudes get exported.
    n_cpus = 12
    fresh_start = False
    for process_mult in process_multiplicities:
        process_in_batches(ampl_folders_prefix, sqampl_raw_folders_prefix, name=process_mult, fresh_start=fresh_start,
                           export_folder=export_folder, n_cpus=n_cpus)
