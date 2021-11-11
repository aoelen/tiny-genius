from utils import make_pool, save_nlp_statements 
from cso_classifier import CSOClassifier

cc = CSOClassifier(
    modules="both",
    enhancement="first",
    explanation=True,
    fast_classification=True,
)

def run_cso_classifier(paper):
    result = cc.run({"title": paper['title'], "abstract": paper['abstract']})
    save_nlp_statements(paper["id"], 'cso-classifier', result)

if __name__ == "__main__":
    make_pool(
        run_tool=run_cso_classifier, 
        tool_name='cso-classifier', 
        overwrite=False, 
        threads=1, 
        field=".*cs.*"
    )