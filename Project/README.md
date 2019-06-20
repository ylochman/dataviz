# Data Visualization Final Project

## Docker
- run an application with Docker:
`docker run -d -p 8050:8050 --rm --name yl-dataviz ylochman/dataviz:latest`
- go to `localhost:8050`
- stop and remove container run:
`docker container stop $(docker container ls -f "name=yl-dataviz" -q)` 

## Heroku
- go to https://yl-dataviz.herokuapp.com