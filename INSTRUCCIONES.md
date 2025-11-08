# Instrucciones de Instalación (Versión Corregida)

¡Hola! Aquí te explico cómo instalar y ejecutar la última versión del programa. El problema con el tema oscuro (`ttkthemes`) ha sido solucionado.

Te recomiendo seguir la **Opción 2** para crear un archivo `.exe` que es más fácil de usar.

---

### **Opción 1: Ejecutar el programa con Python**

1.  **Instalar Python:**
    *   Si aún no lo tienes, descarga e instala **Python 3.8** desde [este enlace oficial](https://www.python.org/ftp/python/3.8.10/python-3.8.10.exe). (Compatible con Windows 7).
    *   **Importante:** Durante la instalación, marca la casilla que dice **"Add Python 3.8 to PATH"**.

2.  **Abrir el Símbolo del sistema (cmd):**
    *   Ve al menú Inicio, busca `cmd` y ábrelo.

3.  **Ir a la Carpeta del Proyecto:**
    *   Usa el comando `cd` para navegar a la carpeta del proyecto. Por ejemplo:
        ```bash
        cd C:\Users\TuUsuario\Desktop\boletas_proyecto
        ```

4.  **Instalar las Dependencias:**
    *   Ejecuta este comando para instalar todas las librerías necesarias:
        ```bash
        pip install -r requirements.txt
        ```

5.  **Iniciar el Programa:**
    *   Una vez instalado todo, ejecuta la aplicación con:
        ```bash
        python src/main.py
        ```

---

### **Opción 2: Crear un archivo `.exe` (Recomendado)**

Este método empaqueta todo en un solo archivo y soluciona el error `No module named 'ttkthemes'`.

1.  **Sigue los Pasos 1, 2 y 3** de la opción anterior.

2.  **Prepara la carpeta `tools` (muy importante):**
    *   Dentro de la carpeta del proyecto, crea una nueva carpeta llamada `tools`.
    *   Descarga la versión portable de SumatraPDF desde [este enlace (64-bit)](https://www.sumatrapdfreader.org/dl/SumatraPDF-3.5.2-64.zip) o [este (32-bit)](https://www.sumatrapdfreader.org/dl/SumatraPDF-3.5.2.zip).
    *   Abre el archivo `.zip` y copia el archivo `SumatraPDF.exe` dentro de la carpeta `tools` que acabas de crear.

3.  **Instalar PyInstaller:**
    *   Si no lo tienes instalado, usa este comando:
        ```bash
        pip install pyinstaller
        ```

4.  **Crear el Ejecutable (Comando Actualizado):**
    *   Usa este nuevo comando en `cmd`. La parte `--hidden-import=ttkthemes` le dice a PyInstaller que incluya la librería del tema oscuro, solucionando el error.
        ```bash
        pyinstaller --windowed --onefile --hidden-import=ttkthemes --add-data "assets;assets" --add-data "tools;tools" src/main.py
        ```

5.  **¡Listo!**
    *   Al terminar, se creará una nueva carpeta llamada `dist`.
    *   Dentro de `dist`, encontrarás **`main.exe`**. Este es tu programa final, con el tema oscuro funcionando.

---

Con este nuevo comando, el problema debería estar resuelto. Si tienes alguna otra duda, ¡aquí estoy!
