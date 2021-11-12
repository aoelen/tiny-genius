from mongo import collection_papers, collection_properties, collection_resources
import multiprocessing as mp
import time

def save_nlp_statements(paper_id, tool_name, data):
    filter = {"id": paper_id}
    print('Paper ID', paper_id)
    updated_data = {
        "$set": {
            f"nlp_results.{tool_name}": data,
        }
    }
    
    collection_papers.update_one(filter, updated_data)

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

    print('Finished, time elapsed:', end - start)
