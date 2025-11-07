# Instrucciones de Instalación

¡Hola! Aquí te explico cómo puedes instalar y ejecutar el programa en tu computadora con Windows.

Tienes dos opciones principales:

1.  **Ejecutarlo usando Python:** Esto es útil si quieres hacer pruebas o modificaciones.
2.  **Crear un archivo `.exe`:** Esta es la mejor opción para el uso diario. Crea un archivo único que puedes abrir con doble clic, sin necesidad de comandos ni de tener Python instalado en otras máquinas.

---

### **Opción 1: Ejecutar el programa con Python**

1.  **Instalar Python:**
    *   Si aún no lo tienes, descarga e instala **Python 3.8** (la última versión compatible con Windows 7) desde [este enlace](https://www.python.org/ftp/python/3.8.10/python-3.8.10.exe).
    *   **Muy importante:** Durante la instalación, asegúrate de marcar la casilla que dice **"Add Python 3.8 to PATH"**.

2.  **Abrir la Terminal (Símbolo del sistema):**
    *   Haz clic en el menú Inicio, busca `cmd` y abre el "Símbolo del sistema".

3.  **Navegar a la Carpeta del Proyecto:**
    *   Usa el comando `cd` para ir a la carpeta donde tienes los archivos del programa. Por ejemplo, si está en tu Escritorio, escribirías:
        ```bash
        cd C:\Users\TuUsuario\Desktop\nombre-de-la-carpeta-del-proyecto
        ```

4.  **Instalar las Dependencias:**
    *   Ahora, instala todas las librerías que el programa necesita con este comando:
        ```bash
        pip install -r requirements.txt
        ```

5.  **Ejecutar el Programa:**
    *   Una vez que termine la instalación, puedes iniciar la aplicación con:
        ```bash
        python src/main.py
        ```

---

### **Opción 2: Crear un archivo `.exe` (Recomendado)**

Este método empaqueta todo en un solo archivo para que sea fácil de usar y distribuir.

1.  **Sigue los Pasos 1, 2 y 3** de la opción anterior para instalar Python y abrir la terminal en la carpeta correcta.

2.  **Instalar PyInstaller:**
    *   PyInstaller es la herramienta que convierte el código en un `.exe`. Instálala con este comando:
        ```bash
        pip install pyinstaller
        ```

3.  **Crear el Ejecutable:**
    *   Asegúrate de estar en la carpeta raíz del proyecto en la terminal. Ahora, ejecuta el siguiente comando. Este le indica a PyInstaller que cree un solo archivo, que es una aplicación de ventana (sin consola negra detrás) y que incluya los recursos necesarios (como el logo y la herramienta de impresión):
        ```bash
        pyinstaller --windowed --onefile --add-data "assets;assets" --add-data "tools;tools" src/main.py
        ```
    *   Este proceso puede tardar unos minutos.

4.  **Encontrar tu Programa:**
    *   Una vez que termine, verás una nueva carpeta llamada `dist` dentro de la carpeta de tu proyecto.
    *   Abre la carpeta `dist` y adentro encontrarás **`main.exe`**.
    *   ¡Ese es tu programa! Puedes copiar este archivo a tu Escritorio o a cualquier otra parte de tu PC. Ya no necesitarás los demás archivos para ejecutarlo.

---

Espero que estas instrucciones te sean de gran ayuda. ¡Si tienes alguna otra pregunta, no dudes en consultarme!
