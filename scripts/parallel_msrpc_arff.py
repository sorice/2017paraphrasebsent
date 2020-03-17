from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd
from pandas import DataFrame, Series, read_table
import time
import textsim
from textsim.utils import calc_all

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
    
def return_obj(row, sent1, sent2, clase):
    try:
        obj = calc_all(sent1,sent2)[2:]
        sec = ''
        for item in obj:
            if str(item) == 'nan':
                sec += '?,'
            else:
                sec += str(item)+','
        sec += str(row) #append id for future analysis after classification
        if clase:
            with open('data/MSRPC-2004/msrpc_test_textsim-42fb.arff','a') as corpus: 
                corpus.write(sec+',yes\n')
        else:
            with open('data/MSRPC-2004/msrpc_test_textsim-42fb.arff','a') as corpus: 
                corpus.write(sec+',no\n')

    except:
        return row

if __name__=='__main__':
	#Read Paraphrase Corpus
	df = read_table('data/MSRPC-2004/msrpc.txt',sep='\t')

	distances = []
	exceptions = []
	ti = time.time()
	#Open vector similarity feature corpus
	with open('data/MSRPC-2004/msrpc_test_textsim-42fb.arff','w') as corpus: 
		corpus.write('@relation paraphrase\n\n')
		for distance in sorted(textsim.__all_distances__.keys()):
			corpus.write('@attribute '+distance+' numeric\n')
			distances.append(distance)
		corpus.write('@attribute '+'id'+' integer\n')
		distances.append('id')
		corpus.write('@attribute class {yes,no}\n\n')
		distances.append('class')
		corpus.write('@data\n')

	#Parallel trick for this problem
	arr = [{'row':i, 'sent1':df.xs(i)[3], 'sent2':df.xs(i)[4], 'clase':df.xs(i)[0]} for i in range(len(df))]
	exceptions = parallel_process(arr, return_obj, use_kwargs=True)
		
	tf = time.time()-ti
	print('Total time:',tf)
