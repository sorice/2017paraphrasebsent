from concurrent.futures import ProcessPoolExecutor, as_completed
import textsim
from textsim.utils import calc_all
from tqdm import tqdm
import os

def return_obj(row, sent1, sent2, clase):
    """Generic function to calculate all the similar distances by row.

    :Note: The corpus in which you must write the results of every
    calculated vector must be set by hand"""
    try:
        obj = calc_all(sent1,sent2)[2:]
        sec = ''
        for item in obj:
            if str(item) == 'nan':
                sec += 'nan,'
            elif item == '':
                sec += 'nan,'
            else:
                sec += str(item)+','
        
        #Append id for future analysis after classification
        sec += str(row) 
        
        #Append class number
        if clase=='1':
            sec+='1'
        else:
            sec+='0'

        with open('data/MSRPC-2004/parallel_msrpc.csv','a') as corpus: 
                corpus.write(sec+'\n')
            
    except:
        return row

def parallel_process(array, function, n_jobs=4, use_kwargs=False, front_num=3):
    """
        A parallel version of the map function with a progress bar. 

        Args:
            array (array-like): An array to iterate over.
            function (function): A python function to apply to the elements of array
            n_jobs (int, default=16): The number of cores to use
            use_kwargs (boolean, default=False): Whether to consider the elements of array as dictionaries of 
                keyword arguments to function 
            front_num (int, default=3): The number of iterations to run serially before kicking off the parallel job. 
                Useful for catching bugs
        Returns:
            [function(array[0]), function(array[1]), ...]
    """
    
    #We run the first few iterations serially to catch bugs
    if front_num > 0:
        front = [function(**a) if use_kwargs else function(a) for a in array[:front_num]]
    
    #If we set n_jobs to 1, just run a list comprehension. This is useful for benchmarking and debugging.
    if n_jobs==1:
        return front + [function(**a) if use_kwargs else function(a) for a in tqdm(array[front_num:])]
    
    #Assemble the workers
    with ProcessPoolExecutor(max_workers=n_jobs) as pool:
        #Pass the elements of array into function
        if use_kwargs:
            futures = [pool.submit(function, **a) for a in array[front_num:]]
        else:
            futures = [pool.submit(function, a) for a in array[front_num:]]
        kwargs = {
            'total': len(futures),
            'unit': 'it',
            'unit_scale': True,
            'leave': True
        }
        #Print out the progress as tasks complete
        for f in tqdm(as_completed(futures), **kwargs):
            pass
    out = []
    #Get the results from the futures. 
    for i, future in tqdm(enumerate(futures)):
        try:
            out.append(future.result())
        except Exception as e:
            out.append(e)
    return front + out