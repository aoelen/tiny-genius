from mongo import collection_papers, collection_properties, collection_resources
import multiprocessing as mp
import time
from itertools import repeat

bulk = collection_papers.initialize_unordered_bulk_op()
counter = 0

def save_nlp_statements(paper_id, tool_name, data, is_last_run):
    global bulk
    global counter

    print('Paper ID: ', paper_id)

    updated_data = {
        "$set": {
            f"nlp_results.{tool_name}": data,
        }
    }
    
    bulk.find({ 'id': paper_id }).update(updated_data)
    counter += 1

    if (counter % 500 == 0 or is_last_run):
        bulk.execute()
        bulk = collection_papers.initialize_ordered_bulk_op()

def make_pool(run_tool, tool_name, overwrite=False, threads=1, field=".*"):
    print(f'Start running {tool_name}, on {threads} threads')

    start = time.time()
    process_papers = True

    # once done processing, start again (not used to parallelization)
    while process_papers:
        print('Creating new batches...')
        filter = {
            f"nlp_results.{tool_name}": { "$exists": overwrite },
            "categories": { "$regex" : field }
        }

        papers = list(collection_papers.find(filter).limit(10000))
        if len(papers) == 0:
            process_papers = False
            break
        
        is_last_run = len(papers) < 10000
        pool = mp.Pool(threads)
        pool.starmap(run_tool, zip(papers, repeat(is_last_run)))
        pool.close()

    end = time.time()

    if (counter % 500 != 0):
        bulk.execute()

    print('Finished, time elapsed:', end - start)
