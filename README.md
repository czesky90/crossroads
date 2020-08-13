# Welcome in crossroads project!

 ## Setup project
 
 ### Prerequisits
 
 * Installed docker and docker-compose on your machine (`sudo dnf install docker docker-compose`)
 * API key for the Google Maps ( https://developers.google.com/maps/documentation/embed/get-api-key )
 * Self signed certificate for HTTPS ( https://linuxize.com/post/creating-a-self-signed-ssl-certificate/ )
 
 ### Prepare environment
 
 Once all prerequisits are met you simply need to:
1. Clone this repo:
 `git clone https://github.com/przypieczony/crossroads.git; cd crossroads`
2. Create file with Google Maps API key and flask key
 ```sh
cat << EOF >> api_keys
export GOOGLEMAPS_KEY=some_key
export FLASK_SECRET_KEY=dupa1234
EOF
```
 3. Put generated certificate (`localhost.crt`) with private key (`localhost.key`) to docker directory. Names of that files must match.
 4. Build docker image:
 `export CR_DOCKER_IMAGE="dev_cr_image"; docker build -f docker/Dockerfile -t "${CR_DOCKER_IMAGE}" .`
 
### Launching application

1. Source credentials:
`source api_keys`
2. Launch application:
 `cd docker; docker-compose up`
3. Application should be available via browser under `localhost` URL
 
*Hint*
> You don't have to repeat all above points in order to launch application.
> After you prepare your environment, you need to only repeat steps from Launching application sectio