# Proyecto de Web Scraping con Django y PostgreSQL

Este proyecto utiliza Django para realizar scraping de datos de una página web y almacenar los resultados en una base de datos PostgreSQL. Utiliza Docker para facilitar el desarrollo y la implementación.

## Requisitos Previos

Asegúrate de tener instalados los siguientes programas en tu máquina local:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/)

## Estructura del Proyecto

- **proyecto_web_scraping/scraper/**: Contiene el proyecto Django.
- **proyecto_web_scraping/scraper/** Contiene el código de la aplicación scraper y los modelos de Django.
- **docker-compose.yml**: Archivo de configuración para Docker Compose.

## Instrucciones para Ejecutar el Proyecto

1. **Clona este repositorio en tu máquina local**:

    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_REPOSITORIO>
    ```

2. **Crea un archivo `.env` en la raíz del proyecto** con las variables de entorno necesarias para la base de datos:

    ```plaintext
    POSTGRES_USER=tu_usuario
    POSTGRES_PASSWORD=tu_contraseña
    POSTGRES_DB=nombre_de_la_base_de_datos
    ```

3. **Construye y ejecuta los contenedores** utilizando Docker Compose:

    ```bash
    docker-compose up --build
    ```

    Este comando construirá las imágenes necesarias y levantará los contenedores especificados en el archivo `docker-compose.yml`.

4. **Verifica que el scraper esté ejecutándose**. El scraper realizará migraciones y comenzará a extraer datos de la página web.

5. **Accede a la base de datos PostgreSQL** dentro del contenedor de la base de datos:

    ```bash
    docker exec -it <NOMBRE_DEL_CONTENEDOR_DB> psql -U <tu_usuario> -d <nombre_de_la_base_de_datos>
    ```

## Descripción de los Servicios Utilizados

### Scraper

- **Descripción**: Este servicio utiliza Python y Django para realizar scraping de datos de una página web específica. Los datos extraídos se guardan en una base de datos PostgreSQL.
- **Dependencias**: Depende del servicio de base de datos (`db`) para funcionar correctamente.
- **Comando**: Se ejecuta con el comando `python manage.py makemigrations && python manage.py migrate && python manage.py run_scraper`.

### Base de Datos

- **Descripción**: Este servicio utiliza PostgreSQL como base de datos para almacenar los datos extraídos por el scraper.
- **Imagen**: Utiliza la imagen oficial de PostgreSQL versión 13.
- **Persistencia**: Los datos son persistentes gracias al volumen `postgres_data`, que guarda los datos en la máquina local.

## Acceso a los Datos

Una vez que el scraper ha completado su ejecución, los datos se almacenarán en la base de datos PostgreSQL. Puedes acceder a los datos utilizando una herramienta de administración de bases de datos como `pgAdmin` o directamente desde la línea de comandos utilizando `psql`.

Para acceder a los datos desde el contenedor de PostgreSQL, utiliza el siguiente comando:

```bash
docker exec -it <NOMBRE_DEL_CONTENEDOR_DB> psql -U <tu_usuario> -d <nombre_de_la_base_de_datos>
