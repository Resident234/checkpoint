
from checkpoint.errors import CheckPointKnowledgeError
from checkpoint.knowledge.pages import urls


def get_url_of_page(page: str) -> str:
    if page not in urls:
        raise CheckPointKnowledgeError(f'The page "{page}" has not been found in CheckPoint\'s pages knowledge.')
    return urls.get(page)
