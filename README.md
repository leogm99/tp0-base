# TP0: Ej1.1

El script que genera N configuraciones de cliente se encuentra en el directorio `scripts` con el nombre `gen_docker_compose_n_clients.py`.
Lo unico que se requiere para correrlo es un interprete de Python>=3.8.


**IMPORTANTE**: El script sobreescribe el file original.

Ejemplo de ejecucion:

```
  python3 gen_docker_compose_n_clients.py -n 5 -f ../docker-compose-dev.yaml
```