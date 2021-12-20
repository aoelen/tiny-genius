from utils import make_pool, save_nlp_statements 
from cso_classifier import CSOClassifier

cc = CSOClassifier(
    modules="both",
    enhancement="first",
    explanation=True,
    fast_classification=True,
)

def run_cso_classifier(paper, is_last_run):
    result = cc.run({"title": paper['title'], "abstract": paper['abstract']})
    save_nlp_statements(paper["id"], 'cso_classifier', result, is_last_run)

if __name__ == "__main__":
    make_pool(
        run_tool=run_cso_classifier, 
        tool_name='cso_classifier', 
        overwrite=False, 
        threads=25,
        field=".*cs.LG.*"
    )