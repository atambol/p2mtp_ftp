#### DESCRIPTION
This project implements point-to-multipoint reliable data transfer protocol using the Stop-and-Wait automatic repeat request (ARQ) scheme. Click [here](https://github.com/atambol/p2mtp_ftp/blob/master/description.pdf) for a detailed description.


#### INSTRUCTIONS TO RUN
Running the server:
```
python p2mpserver.py <server-port#> <file-name> <loss-probability>
```
> Example: python p2mpserver.py 7735 received.txt .01

Running the client:
```
python p2mpclient.py <server-address-list> <server-port#> <file-name> <MSS>
```
> Example: python p2mpclient.py localhost 7735 send.txt 500
