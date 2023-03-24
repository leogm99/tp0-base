# TP0: Ej7

Ejecutar este ejercicio requiere primero copiar los datos de las agencias mediante el script 
`move_data_to_client.sh`, luego levantar los servicios mediante `make docker-compose-up` y por ultimo
observar los logs mediante `make docker-compose-logs`, donde veremos la cantidad de ganadores de cada agencia.

A este ejercicio se le agrega soporte para procesar las bets luego de haberlas recibido. Se extiende el protocolo
para soportar el envio de los DNIS ganadores a cada agencia.

El server, luego de haber recibido las apuestas de todas las agencias, debe decidir a que agencia enviar cada bet.
Para esto, lee primero de las apuestas recibidas el agencyID, que por la manera serial en la que está programado,
identifica univocamente a que socket se le deberá enviar las apuestas.

Luego, lee las apuestas mediante la funcion `load_bets` y filtra aquellas apuestas que sean de la agencia actual,
mappeando el documento unicamente.

La extension del protocolo resulta en los siguientes paqutes:

```
    |-------------|
    |   nWinners  |
    |-------------|
    /   4 bytes   /

```

```
    |--------------|----------------|
    | document-len |    document    |
    |--------------|----------------|
    /   2 bytes    /  doc-len bytes /

```

El servidor entonces envia 4 bytes que indican cuantos ganadores se deberan leer. Por cada ganador, necesitamos 
leer su documento, que como se representa como un string, incluye 2 bytes de largo.
