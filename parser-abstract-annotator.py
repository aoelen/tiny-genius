from utils import make_pool, save_nlp_statements 
import requests

def run_abstract_annotator(paper, is_last_run):
    data = {"text2annotate": paper['abstract']}
    response = requests.post(url="http://annotation:5000/annotator/", json=data)
    data = response.json()["entities"]
    save_nlp_statements(paper["id"], 'abstract_annotator', data, is_last_run)

if __name__ == "__main__":
    make_pool(
        run_tool=run_abstract_annotator, 
        tool_name='abstract_annotator', 
        overwrite=False, 
        threads=1, 
        field=".*cs.LG.*"
    )
