from utils import make_pool, save_nlp_statements 
import requests

def run_abstract_annotator(paper):
    data = {"text2annotate": paper['abstract']}
    response = requests.post(url="http://annotation:5000/annotator/", json=data)
    data = response.json()["entities"]
    save_nlp_statements(paper["id"], 'abstract_annotator', data)

if __name__ == "__main__":
    make_pool(
        run_tool=run_abstract_annotator, 
        tool_name='abstract_annotator', 
        overwrite=False, 
        threads=10, 
        #field=".*cs.HC.*"
    )
