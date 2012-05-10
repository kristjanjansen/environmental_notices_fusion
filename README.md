## About 

Here's the code powering the public service http://keskkonnateated.ee

## Installing

It's assumed that you have virtualenv and Foreman installed.

```
git clone https://github.com/kristjanjansen/environmental_notices
cd environmental_notices
virtualenv venv --distribute
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create environment file
```
touch .env
```

Insert following values to the ```.env``` file:
```
GOOGLE_USERNAME=your_google_username
GOOGLE_PASSWORD=your_google_password
GEONAMES_USERNAME=your_geonames_username
GOOGLE_FUSION_ID=your_google_fusion_table_id
GOOGLE_ANALYTICS_ID=your_google_analytics_id
```

(Analytics ID is optional)


## Run Locally

### Backend

Run
```
foreman start worker
```

Alternatively you can add required config vars to ```~/.bashrc``` and run ```python worker.py``` , more information here: http://devcenter.heroku.com/articles/config-vars

Then run

```
foreman start web
```

## Run in Heroku

First deploy http://devcenter.heroku.com/articles/python#deploy_to_herokucedar and set up config:

```
heroku config:add GOOGLE_USERNAME=your_google_username GOOGLE_PASSWORD=your_google_password GEONAMES_USERNAME=your_geonames_username GOOGLE_FUSION_ID=your_google_fusion_table_id
GOOGLE_ANALYTICS_ID=your_google_analytics_id
```

Then set up worker task using scheduler (and test it using "Run now"):
```
python worker.py
```

Then run
```
heroku open
```