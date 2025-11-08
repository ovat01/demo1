# Instrucciones Finales de Instalación y Optimización

¡Hola! Esta es la guía definitiva para crear la versión más rápida y profesional del programa.

He solucionado los dos problemas que mencionaste:
1.  **Error `No module named 'ttkthemes'`:** Corregido permanentemente.
2.  **Lentitud al abrir el `.exe`:** Solucionado con un nuevo método de compilación.

Por favor, sigue estas instrucciones. **El Método 2 es el recomendado para la versión final.**

---

### **Método 1: Ejecutar con Python (para pruebas)**

1.  **Instalar Python 3.8:** [Descarga desde aquí](https://www.python.org/ftp/python/3.8.10/python-3.8.10.exe). Marca **"Add Python 3.8 to PATH"** al instalar.
2.  **Abrir `cmd` (Símbolo del sistema).**
3.  **Navegar a la carpeta del proyecto** con el comando `cd`.
4.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Ejecutar:**
    ```bash
    python src/main.py
    ```

---

### **Método 2: Crear un Ejecutable Optimizado (Recomendado)**

Este método crea una **carpeta** con el `.exe` y sus archivos. Es el estándar profesional y hace que el programa **abra instantáneamente**.

1.  **Sigue los Pasos 1, 2 y 3** del método anterior.

2.  **Prepara la carpeta `tools` (Paso crucial):**
    *   Dentro de la carpeta del proyecto, crea una carpeta llamada `tools`.
    *   Descarga la versión portable de SumatraPDF desde [este enlace (64-bit)](https://www.sumatrapdfreader.org/dl/SumatraPDF-3.5.2-64.zip).
    *   Copia el archivo `SumatraPDF.exe` del `.zip` a tu nueva carpeta `tools`.

3.  **Instalar PyInstaller:**
    *   `pip install pyinstaller`

4.  **Crear el Ejecutable (Comando Final Optimizado):**
    *   Usa este nuevo comando. **He quitado `--onefile`** para ganar velocidad.
        ```bash
        pyinstaller --windowed --hidden-import=ttkthemes --add-data "assets;assets" --add-data "tools;tools" --name "ReimpresorBoletas" src/main.py
        ```
    *   También he añadido `--name "ReimpresorBoletas"` para que el `.exe` tenga un nombre más profesional.

5.  **Encuentra y Usa tu Programa:**
    *   Al terminar, se creará una carpeta `dist`.
    *   Dentro de `dist`, verás una **nueva carpeta** llamada `ReimpresorBoletas`. **Esta carpeta es tu programa.**
    *   Puedes copiar esta carpeta completa a tu Escritorio o a donde quieras. Para abrir el programa, simplemente haz doble clic en el archivo `ReimpresorBoletas.exe` que está **dentro** de esa carpeta.

**Para distribuir el programa a otros equipos, solo tienes que copiar y pegar la carpeta `ReimpresorBoletas` completa.**

---

Con estos cambios, el programa debería funcionar a la perfección. ¡Avísame qué tal te va!
