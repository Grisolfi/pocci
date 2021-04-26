from git import Repo
from tempfile import mkdtemp
from os import getcwd


def clone_to_temp(url=None, full_repo_name=None, x_token=None, ref=None):
    if not url and full_repo_name:
        url = f'https://x-access-token:{x_token}@github.com/{full_repo_name}.git'

    temp_dir = mkdtemp(
        prefix='ci-server-',
        dir=getcwd()
    )

    repo = Repo.clone_from(
        url = url,
        to_path = temp_dir
    )
    
    if ref:
        repo.git.checkout(ref)

    return temp_dir, repo

    


    



