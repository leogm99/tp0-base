# TP0: Ej6

Para ejecutar este ejercicio primero deberemos ejecutar el script `move_data_to_client.sh` 
para copiar los datos de las agencias al directorio del cliente.

`
    sh scripts/move_data_to_client.sh
`
Luego, podemos levantar todo ejecutando `make docker-compose-up`.

Para este ejercicio, se extiende el modelo anterior para habilitar
el envio de apuestas en batch, de tal manera de reducir los tiempos de
transmision y de procesamiento.

Los clientes siguen manteniendo la misma estructura para los paquetes de datos de las bets:

```
    |------------|----------------|-----------|-----------------|--------------|-------------------|--------------|------------------|----------|---------|
    |  name-len  |      name      |surname-len|     surname     | document-len |     document      | birthdate-len|     birthdate    |bet number|agency-id|
    |------------|----------------|-----------|-----------------|--------------|-------------------|--------------|------------------|----------|---------|
    /   2 bytes  / name-len bytes /  2 bytes  /surname-len bytes/    2 bytes   /document-len bytes /    2 bytes   /  birth-len bytes / 2 bytes /  1 byte /
    
```

Pero, al enviar un batch, lo que se hace es prependear 4 bytes con la cantidad de bets por batch:

```
    |-----------------|
    | n_batch_elements|
    |-----------------|
    /     4 bytes     /
```

La cantidad de elementos por batch es configurable desde el `.yaml` de cliente.

Cuando se envia todo el batch, debemos notificar al servidor si seguir escuchando o no (capaz quedan batches por enviar),
por ende, appendeamos 1 byte que sirva de señal para notificarle esto al servidor.

```
    |----------------|
    | keep_listening |
    |----------------|
    /     1 byte     /
```
Si el byte recibido es 0x1, el server esperará por nuevos batches. Caso contrario, dejara de escuchar por socket.

