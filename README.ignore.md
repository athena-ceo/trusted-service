Ignore the following:

> **2. Port numbers**
> 
> It is advised to have specific port numbers per locale to allow several images to run simultaneously.
> Trusted Service is adopting the following convention:
> [backend](src/backend)
>   | Locale | http port | https port |
>   |--------|-----------|------------|
>   | en_US  | 9060      | 9443       |
>   | fr_FR  | 9061      | 9444       |
> 
> The port specified in the docker command (option `-p`) should match the `decision_service_url` option in tab `odm`

