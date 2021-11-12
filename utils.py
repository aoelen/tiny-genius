from mongo import collection_papers, collection_properties, collection_resources
import multiprocessing as mp
import time

bulk = collection_papers.initialize_unordered_bulk_op()
counter = 0

def save_nlp_statements(paper_id, tool_name, data):
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

    if (counter % 500 == 0):
        bulk.execute()
        bulk = collection_papers.initialize_ordered_bulk_op()

def make_pool(run_tool, tool_name, overwrite=False, threads=1, field=".*"):
    print(f'Start running {tool_name}, on {threads} threads')

    start = time.time()
    process_papers = True

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

        pool = mp.Pool(threads)
        pool.map(run_tool, papers)
        pool.close()
    
    end = time.time()

    if (counter % 500 != 0):
        bulk.execute()

    print('Finished, time elapsed:', end - start)
