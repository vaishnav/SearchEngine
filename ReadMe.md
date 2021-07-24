# Welcome to search engine project

### Install pipenv first
```
    pip3 install pipenv
```

### Installing dependencies 
```
    pipenv lock
```
records the new requirements to the Pipfile.lock file.

```
    pipenv update
```
records the new requirements to the Pipfile.lock file and installs the missing dependencies on the Python interpreter.

```
    pipenv shell
```

starts the python virtual environment

#### NOTE- For any further operation inside virtual environment use "pipenv" instead of "pip"

#### current project is made for wikipedia but i am using xkcd for testing as it has less number of links 

#### for using with wikipedia remove comments from line 7,12 in views.py of engine app

### go to http://127.0.0.1:8000/engine/crawl for seeing crawled results
### go to http://127.0.0.1:8000/engine/rank for seeing ranking results for crawled pages and storing pagerank values inside the database

### go to  http://127.0.0.1:8000/engine/index to view the index page

### go to http://127.0.0.1:8000/engine/indexer for checking if indexing is working fine

### Search suggestion feature added(Suggestons are based upon previous global searches and their order is according to the respective frequencies)- How to test it? 
###----- Search 'program', next time when you search a word that is prefix of 'program', it will be shown in suggestion dropdown
###----- Search 'programming' next time you will see 'program' and 'programming', 
###----- Search 'programming' 2-3 times, and you will see next time 'programming' appears on the top while typing p as it's frequency of search is higher

