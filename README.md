# TP0: Ej3

Para resolver este ejercicio, se genera una imagen de docker usando busybox como base (que ya trae un binario de netcat instalado).

El `script` `test_server.sh` genera N tiras aleatorias de bytes que son enviadas al server a través de netcat, y checkea que la respuesta sea
exactamente la misma que lo que fue enviado.

Para conectar la imagen de busybox a la misma network, se le pasa el flag `--network tp0_testing_net` como parametro a `docker run` de tal modo 
que se pueda hacer resolucion de esa red dentro del container.

Para ejecutar las pruebas, basta simplemente con ejecutar `sh run_tests.sh` dentro del directorio `scripts`.

Luego, para destruir los procesos y liberar los recursos, sera necesario correr `make docker-compose-down en la raiz del proyecto`.