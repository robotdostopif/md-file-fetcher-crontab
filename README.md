# md-file-fetcher



## Setup Project

### Settings config

The project handle local development and production configs and uses environment variables for deployment with docker.

For local development you have to add a dev_config.json file to the src folder of the project.

```json
[
    {
        "database_location": "mongodb+srv://<user>:<password>@cluster.mongodb.net/",
        "database_name": "database_name",
        "collection_name":  "collection_name",
        "database_timeout_ms": 10,
        "git_remote_branch": "remote_branch",
        "git_folder": "git_folder",
        "git_remote_url":"https://<gitlab+deploy-token-key>:<value>@gitlab.com/<gitlabuser>/<repo.git>"
    }
]
```
### Environment variables
```
DATABASE_LOCATION="mongodb+srv://<user>:<password>@cluster.mongodb.net/"  
GIT_REMOTE_URL="https://<gitlab+deploy-token-key>:<value>@gitlab.com/<gitlabuser>/<repo.git>" 
```
### Build Docker

```
docker build -t md-file-fetcher .
```
### Run docker container
```
docker run -e GIT_REMOTE_URL="remote_url" -e DATABASE_LOCATION="database_location" --name md-file-fetcher -it --rm md-file-fetcher
```



### Crontab

The Crontab uses UTC time: https://time.is/sv/UTC therefore the cron interval has to be set corresponding to that.
By default the Crontab script will run every minute.