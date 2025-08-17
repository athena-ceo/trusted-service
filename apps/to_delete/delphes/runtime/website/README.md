# Dummy web site for the prefectures

This web site simulates the prefecture website and introduces the new form.

## Run this website

Look for a script named **start-website.bat|sh** in `..`


## Deploying as a Docker image

From this directory :

### Build the Docker image

```sh
docker build -t delphes-frontend .
```

### Test the Docker image

```sh
docker run -p 8080:8080 delphes-frontend
```

This container **delphes-frontend** is to be invoked together with the other ones thru `docker compose`.