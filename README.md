# TP0: Ej8

Ejecutar este ejercicio requiere primero copiar los datos de las agencias mediante el script 
`move_data_to_client.sh`, luego levantar los servicios mediante `make docker-compose-up` y por ultimo
observar los logs mediante `make docker-compose-logs`, donde veremos la cantidad de ganadores de cada agencia.

En este ejercicio se agrega la capacidad al server de procesar clientes virtualmente en paralelo. El server 
levanta una pool de procesos, que recibe tasks. El primer tipo de task es de tipo `BetReceiver`, en donde se 
escucha por socket las apuestas de cada agencia y se guardan en el archivo de apuestas. Este archivo, que es accedido
de manera concurrente por los multiples procesos de la pool, es protegido mediante file locks para que solamente
uno de esos procesos pueda escribir a la vez. La lectura del archivo, similarmente, es protegida mediante un shared
lock.

El proceso/hilo principal esperará a que todas las agencias hayan terminado de enviar sus apuestas. Esto se logra
esperando a los async results de cada tarea lanzada a la pool. Estos async results a su vez guardan la proxima tarea
a ejecutar, que es la de enviar a cada agencia sus respectivos ganadores. Se vuelven a pasar las tareas a la pool.

Finalmente, se cierra la pool, prohibiendo que se reciban nuevas tareas, y se la joinea para liberar los procesos y
recursos reservados.