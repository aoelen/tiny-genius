from orkg_title_parser.parse_titles import parse_title as orkg_title_parser
from utils import make_pool, save_nlp_statements 
from transformers import pipeline
from mongo import collection_papers, collection_properties, collection_resources

summarizer = pipeline("summarization")

def run_summarizer(paper, is_last_run):

    summary = summarizer(
        paper['abstract'],
        max_length=50,
        min_length=10,
        do_sample=False,
        early_stopping=True,
        length_penalty=2.0,
    )

    save_nlp_statements(paper["id"], 'summarizer', summary, is_last_run)

if __name__ == "__main__":
    filter = {
        f"nlp_results.summarizer": { "$exists": False }
    }

    papers = list(collection_papers.find(filter).limit(10000))

    for paper in papers:
        run_summarizer(paper, True)
