# prepare-ollama

To dowload the Model

```
docker-compose up --build --force-recreate
```

Stop all the containers

```
docker stop $(docker ps -a -q)
```

Remove all the containers

```
docker rm $(docker ps -a -q)
```

Clean all the images

```
docker rmi -f IMAGE_ID
```

The image will be created at output/ollama-deepseek-8b.tar

Load the output in the desire machine

```
docker load -i output/ollama-deepseek-8b.tar
```
