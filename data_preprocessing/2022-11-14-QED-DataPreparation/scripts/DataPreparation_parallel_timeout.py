import sys
import os
from icecream import ic 
import sympy as sp
from tqdm import tqdm
from datetime import datetime
import multiprocessing as mp
import multiprocessing.queues as mpq
import functools
import dill
from typing import Tuple, Callable, Dict, Optional, Iterable

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from source.read_amplitudes import read_amplitudes, read_amplitudes_and_raw_squares, fix_operator_num_args, get_tree, fix_tree, fix_subscript, fix_subscripts, read_amplitudes_and_squares
import sympy as sp

# from source.SympyPrefix import prefix_to_sympy, sympy_to_prefix, sympy_to_hybrid_prefix, simplify_and_prefix, simplify_sqampl
# probably worst way of doing this, but I wanted to import the package SympyPrefix
# that is a few folders up.
# documentation: https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
import importlib.util
spec = importlib.util.spec_from_file_location("SympyPrefix", "../../data_preprocessing/sympy_prefix/source/SympyPrefix.py")
SympyPrefix = importlib.util.module_from_spec(spec)
sys.modules["module.name"] = SympyPrefix
spec.loader.exec_module(SympyPrefix)
prefix_to_sympy = SympyPrefix.prefix_to_sympy
sympy_to_prefix = SympyPrefix.sympy_to_prefix
sympy_to_hybrid_prefix = SympyPrefix.sympy_to_hybrid_prefix
simplify_and_prefix = SympyPrefix.simplify_and_prefix
simplify_sqampl = SympyPrefix.simplify_sqampl
from source.ExpressionsTokensCombiner import combine_m_s, combine_m, shorten_expression

# -------------------------------------------------------------------------------------------  

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
            q_out.put((positioning, sp.sympify(x)))
            # print(f'[{pid}]: {positioning}: timed out ({timeout}s)')
            with open(timeout_logfile, "a") as f:
                f.write("Timed out after "+str(timeout)+" seconds. Argument:" + x + "\n")
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


# -------------------------------------------------------------------------------------------  

# # %%
ampl_folders_prefix = "../../data-generation-marty/QED/out_tmp/ampl/"
# sqampl_folders_prefix = "../QED_AllParticles_IO/out/sq_ampl/"
sqampl_raw_folders_prefix = "../../data-generation-marty/QED/out_tmp/sq_ampl_raw/"
amplitudes_folders_names = ["3to3/"]
amplitudes_folders = [ampl_folders_prefix+a for a in amplitudes_folders_names]
sqamplitudes_raw_folders_names = amplitudes_folders_names
sqamplitudes_folders = [sqampl_raw_folders_prefix+a for a in sqamplitudes_raw_folders_names]
cpus = 18
timeout_s = 60*3   # timeout in seconds
# timeout_s = 0.1   # timeout in seconds

data_folder = "../../data_unique.nosync/"
# data_folder = "dev_data.nosync/"
progress_file = "log/progress_3to3.log"
outfile_amplitudes = data_folder+"QED_amplitudes_TreeLevel_3to3.txt"
outfile_sqamplitudes_simplified =  data_folder+"QED_sqamplitudes_TreeLevel_3to3.txt"
outfile_sqamplitudes_simplified_prefix =  data_folder+"QED_sqamplitudes_TreeLevel_3to3_simplified_shortened_hybridprefix.txt"
timeout_logfile = "log/timeout_log_3to3.log"
start_fresh = True   # overwrite progress_file
batch_size = 200
batch_resume = 0

amplitudes = dict()
sqamplitudes = dict()
for amplitudes_folder, sqamplitudes_folder, name in zip(amplitudes_folders, sqamplitudes_folders, amplitudes_folders_names):
    ic(name)

    amplitudes_files = os.listdir(amplitudes_folder)
    sqamplitudes_files = os.listdir(sqamplitudes_folder)
    ampl, sqampl_raw = read_amplitudes_and_raw_squares(amplitudes_folder, sqamplitudes_folder)

    ampls_prefix = []
    print("Loading amplitudes")
    for exp in tqdm(ampl):
        tree = get_tree(exp)
        tree = fix_tree(tree)
        final_expr = fix_subscripts(tree)
        ampls_prefix.append(final_expr)

    sqampls_prefix = []
    print("Loading squared amplitudes")
    for exp in tqdm(sqampl_raw):
        sqampls_prefix.append(exp)  # not actually prefix yet. Had it here before. TODO
    amplitudes[name] = ampls_prefix
    sqamplitudes[name] = sqampls_prefix

# # %%
all_amplitudes = []
for key in amplitudes.keys():
    for x in amplitudes[key]:
        all_amplitudes.append(x)

all_sqamplitudes = []
for key in sqamplitudes.keys():
    for x in sqamplitudes[key]:
        all_sqamplitudes.append(x)
#
# # %%
ic(len(all_amplitudes))
ic(len(all_sqamplitudes))
#
# # %%
# def get_unique_indices(l):
#     seen = set([0])
#     res = []
#     for i, n in enumerate(l):
#         if n not in seen:
#             res.append(i)
#             seen.add(n)
#     return res
#
# # %%
# all_amplitudes_str = [''.join(a) for a in all_amplitudes]
#
# # %%
# unique_indices = np.unique(all_amplitudes_str, return_index=True, axis=0)[1]
# unique_indices_sq = np.unique(all_sqamplitudes, return_index=True, axis=0)[1]
#
# # %%
# unique_indices.sort()
# unique_indices_sq.sort()
#
# # %%
# ic(len(unique_indices));
# ic(len(unique_indices_sq));
# ic(len(unique_indices_sq) / len(unique_indices));
#
# # %%
# all_amplitudes_unique = [all_amplitudes[i] for i in unique_indices]
# all_sqamplitudes_unique = [all_sqamplitudes[i] for i in unique_indices]
all_amplitudes_unique = all_amplitudes
all_sqamplitudes_unique = all_sqamplitudes
#
num_batches = len(all_amplitudes_unique) // batch_size + 1

if start_fresh:
    print("Starting fresh. Deleting "+progress_file)
    if os.path.exists(progress_file):
        os.remove(progress_file)
    if os.path.exists(outfile_amplitudes):
        print("Deleting "+outfile_amplitudes)
        os.remove(outfile_amplitudes)
    if os.path.exists(outfile_sqamplitudes_simplified):
        print("Deleting "+outfile_sqamplitudes_simplified)
        os.remove(outfile_sqamplitudes_simplified)
    if os.path.exists(outfile_sqamplitudes_simplified_prefix):
        print("Deleting "+outfile_sqamplitudes_simplified_prefix)
        os.remove(outfile_sqamplitudes_simplified_prefix)
    if os.path.exists(timeout_logfile):
        print("Deleting "+timeout_logfile)
        os.remove(timeout_logfile)

    with open(progress_file, 'a') as f:
        f.write("Starting calculation at:"+str(datetime.now())+"\n")
        f.write("Worked on folders:"+"".join(amplitudes_folders_names)+"\n")
        f.write("batch_size:"+str(batch_size)+"\n")
        f.write("lines:"+str(len(all_amplitudes_unique))+"\n")
        f.write("num_batches:"+str(num_batches)+"\n")
        f.write("----------------------\n")
        f.write("----------------------\n")

else:
    print("Resuming calculations, reading progress from "+progress_file)
    with open(progress_file) as f:
        progess_file_contents = [line for line in f.readlines()]
    # print(progess_file_contents[-6:])
    batch_resume = int(progess_file_contents[-7].split(":")[1]) + 1
    index_resume = int(progess_file_contents[-3].split(":")[1])
    batch_size_resume = int(progess_file_contents[-2].split(":")[1])
    assert batch_resume*batch_size_resume == index_resume
    batch_size = batch_size_resume
    ic(batch_resume)
    ic(index_resume)
    ic(batch_size_resume)
    print("Continuing with batch " +str(batch_resume)+"/"+str(num_batches)+", which amounts to line "+str(index_resume)+".")
    if batch_resume == num_batches:
        print("Nothing to resume, already finished.")

batches = range(batch_resume, num_batches)

print("Simplifying amplitudes in batches of "+str(batch_size)+":")
for batch in tqdm(batches):
    batch_start_index = batch*batch_size
    batch_end_index = (batch+1)*batch_size
    sqamplitudes_batch = all_sqamplitudes_unique[batch_start_index:batch_end_index]
    amplitudes_batch = all_amplitudes_unique[batch_start_index:batch_end_index]
    # print("batch:", batch, "/", len(batches))

    start_time = datetime.now()
    # ------------------------------

    sqamplitudes_simplified_batch = killer_pmap(simplify_sqampl, sqamplitudes_batch, cpus=cpus, timeout=timeout_s)
    sqamplitudes_simplified_shortened_batch = killer_pmap(shorten_expression, sqamplitudes_simplified_batch, cpus=cpus, timeout=timeout_s)
    # sqamplitudes_simplified_shortened_batch_prefix = killer_pmap(sympy_to_hybrid_prefix, sqamplitudes_simplified_shortened_batch, cpus=cpus, timeout=timeout_s)

    # ------------------------------
    out_amplitudes_str = [",".join(x) for x in amplitudes_batch]
    out_amplitudes_str = "\n".join(out_amplitudes_str)+"\n"
    out_sqamplitudes_simplified_str = [str(x) for x in sqamplitudes_simplified_batch]
    out_sqamplitudes_simplified_str = "\n".join(out_sqamplitudes_simplified_str)+"\n"   # not prefix! Just simplified
    # out_sqamplitudes_prefix_str = [",".join(x) for x in sqamplitudes_simplified_shortened_batch_prefix]
    # out_sqamplitudes_prefix_str = "\n".join(out_sqamplitudes_prefix_str)+"\n"


    with open(outfile_amplitudes, "a") as f:
        f.write(out_amplitudes_str)
    with open(outfile_sqamplitudes_simplified, "a") as f:
        f.write(out_sqamplitudes_simplified_str)
    # with open(outfile_sqamplitudes_simplified_prefix, "a") as f:
        # f.write(out_sqamplitudes_prefix_str)

    # ------------------------------
    end_time = datetime.now()


    with open(progress_file, 'a') as f:
        f.write("Appended amplitudes to "+outfile_amplitudes+"\n")
        f.write("Appended simplified sqamplitudes to "+outfile_sqamplitudes_simplified+"\n")
        f.write("Appended simplified sqamplitudes in prefix notation to "+outfile_sqamplitudes_simplified_prefix+"\n")
        f.write("batch:" + str(batch) + "\n")
        f.write("started at:" + str(start_time) + "\n")
        f.write("finished at:" + str(end_time) + "\n")
        f.write("batch_start_index:" + str(batch_start_index) + "\n")
        f.write("batch_end_index:" + str(batch_end_index) + "\n")
        f.write("batch_size:" + str(batch_size) + "\n")
        f.write("----------------------\n")
