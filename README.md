# TP0: Ej5

En este ejercicio se desarrollo un protocolo de comunicacion binario para cubrir el modelo de dominio
de las agencias y las loterias.

Los clientes (representando a las agencias), envian paquetes con el siguiente formato:

```
    |------------|----------------|-----------|-----------------|--------------|-------------------|--------------|------------------|----------|---------|
    |  name-len  |      name      |surname-len|     surname     | document-len |     document      | birthdate-len|     birthdate    |bet number|agency-id|
    |------------|----------------|-----------|-----------------|--------------|-------------------|--------------|------------------|----------|---------|
    /   2 bytes  / name-len bytes /  2 bytes  /surname-len bytes/    2 bytes   /document-len bytes /    2 bytes   /  birth-len bytes / 2 bytes /  1 byte /
    
```

Los datos de tamaño variable son precedidos por 2 bytes que indican la cantidad de bytes a leer por socket. Estos tamaños son enviados
con el endianess de la network (big endian) y luego se vuelven a pasar al endianess local.

El servidor (representando a la loteria) recibe las apuestas, las persiste mediante la funcion `store_bets` y luego envía un unico byte,
indicando si se pudo persistir o no la informacion:

```
    |-----------|
    | bet state |
    |-----------|
    /  1 byte   /
```
El estado de una bet puede ser 0: Ok o 1: Error.

La deserialización de bytes en python se realiza mediante structure packing.

El control de tamaño de paquetes se realiza splitteando los buffers de la aplicacion en paquetes de 8kb o menos 
(configurable tanto en servidor como en el cliente).

Los issues de short reads y short writes son manejados en ambas aplicaciones mediante wrappers en las funciones de socket correspondientes.

La manera de testear el correcto funcionamiento es levantando los servicios con `make docker-compose-up`, y luego de un tiempo, 
attachearse al server mediante `docker exec -it server /bin/bash`, en donde encontraremos el file `bets.csv`, que debería tener las apuestas
que fueron guardadas correctamente.