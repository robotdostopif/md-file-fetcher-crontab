import git
import os
import markdown
import log
import json
import time
from datetime import datetime
from Database import Database
from pymongo import MongoClient
from bs4 import BeautifulSoup
from pathlib import Path

logger = log.get_logger(__name__)

def get_environment():
    environment_config_path = None
    if os.path.exists('src/dev_config.json'):
        environment_config_path = "dev_config.json"
    else:
        environment_config_path = "prod_config.json"
    
    return environment_config_path

def read_config_file(path):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    config_path = Path(path)
    config = None
    with open(config_path) as config_file:
        config = json.load(config_file)[0]
    return config

def initialize_git_repo(config, close=False):
    if not os.path.exists(config['git_folder']):
        logger.info("Cloning repo")
        git.Repo.clone_from(config['git_remote_url'], config['git_folder'])
        
    repo = git.Repo(config['git_folder'])
    
    if len(repo.remotes) == 0:
        logger.info("Adding remote origin url")
        repo.create_remote('origin', config['git_remote_url'])
    
    logger.info("Reset --hard to latest commit")
    repo.git.reset('--hard')
    return repo
 
def pull_from_repo(config, repo):   
    remote_branch = config['git_remote_branch']
    
    logger.info("Fetching branches from origin")
    repo.remotes.origin.fetch(remote_branch)
    
    logger.info(f"Checkout {remote_branch}")
    repo.git.checkout(remote_branch)
    
    logger.info(f"Pull from {repo.active_branch}")
    repo.remotes.origin.pull(remote_branch)

def get_created_date_from_file(config, test_file_name, repo):
    commits = repo.iter_commits('--all', paths=test_file_name)
    dates = []
    for commit in commits:
        dates.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(commit.committed_date)))
    sorted_dates = sorted([datetime.strptime(dt, "%Y-%m-%d %H:%M:%S") for dt in dates])
    if sorted_dates:
        return sorted_dates[0].strftime("%Y-%m-%d %H:%M:%S")
    else:
        return None 
    
def get_last_updated_date_from_file(config, test_file_name, repo):
    
    commits = repo.iter_commits('--all', paths=test_file_name)
    dates = []
    for commit in commits:
        dates.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(commit.committed_date)))
    
    sorted_dates = sorted([datetime.strptime(dt, "%Y-%m-%d %H:%M:%S") for dt in dates])
    if sorted_dates:
        return sorted_dates[-1].strftime("%Y-%m-%d %H:%M:%S")
    else:
        return None 
    
def load_article_from_file(article_file, config):
        html = markdown.markdown(open(config['git_folder'] + "/" + test_file).read())
        parsed_html = BeautifulSoup(html, features="html.parser").get_text()
        return parsed_html

def load_all_articles(config, repo):
    article_files = os.listdir(config['git_folder'] + "/")
    results = []
    for article_file in article_files:
        if article_file.endswith(".md"):
            created = get_created_date_from_file(config, article, repo)
            last_updated = get_last_updated_date_from_file(config, article_file, repo)
            article = load_article_from_file(article_file, config)
            dict_result = {"file_name": article_file, "file_content":article, "created":created, "last_updated":last_updated, "outdated":False}
            results.append(dict_result)
    return results
def check_outdated(config, articles):
    articles = os.listdir(config['git_folder'] + "/")

    results = []
    for article in articles:
        if article['file_name'] not in articles and not article['outdated']:
            results.append({"file_name":manual_test['file_name'],"outdated":True})
            
    return results
    
def read_env_variables(config):
    config['git_remote_url'] = config['git_remote_url'] if 'git_remote_url' in config.keys() else os.getenv('GIT_REMOTE_URL')
    return config
def run():
    config_path = get_environment()
    config = read_config_file(config_path)
    config_with_env_variables = read_env_variables(config)
    repo = initialize_git_repo(config_with_env_variables)
    pull_from_repo(config_with_env_variables, repo)
    
    database = Database(config_with_env_variables)
    articles = load_all_articles(config_with_env_variables, repo)
    
    for article in articles:
        database.insert_article(article)
        
    articles = database.load_all_articles()
    outdated_articles = check_outdated(config_with_env_variables, articles)
    
    for outdated_article in outdated_articles:
        database.update_outdated_file(outdated_article)
        
    logger.info("Delete remote origin")
    repo.delete_remote('origin')
    
if __name__ == "__main__":
    run()