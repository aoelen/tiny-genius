from orkg_title_parser.parse_titles import parse_title as orkg_title_parser
from utils import make_pool, save_nlp_statements 

def run_title_parser(paper, is_last_run):
    try:
        parsed_title = orkg_title_parser(paper["title"])
    except:
        parsed_title = {}
    
    save_nlp_statements(paper["id"], 'orkg_title_parser', parsed_title, is_last_run)

if __name__ == "__main__":
    make_pool(
        run_tool=run_title_parser, 
        tool_name='orkg_title_parser', 
        overwrite=False, 
        threads=25, 
        field=".*cs.LG.*"
    )
