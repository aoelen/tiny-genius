from utils import make_pool, save_nlp_statements 
import requests

def run_ambiverse_nlu(paper):
    data = {"text": paper['abstract'], "extractConcepts": "true", "language": "en"}
    response = requests.post(url="http://nlu:8080/factextraction/analyze", json=data)
    data = response.json()
    save_nlp_statements(paper["id"], 'ambiverse_nlu', data)

if __name__ == "__main__":
    make_pool(
        run_tool=run_ambiverse_nlu, 
        tool_name='ambiverse_nlu', 
        overwrite=False, 
        threads=10, 
        #field=".*cs.HC.*"
    )
