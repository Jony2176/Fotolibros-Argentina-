# **Manual de Operación: Editor de Fotolibros FDF para Agentes IA**

Este documento sirve como instrucción maestra para que un agente de navegación web (IA) comprenda, localice y opere el editor de Fábrica de Fotolibros (FDF).

## **1\. Mapa de la Interfaz (Coordenadas y Secciones)**

El editor se divide en cuatro áreas críticas que el agente debe monitorear constantemente:

| Sección | Ubicación | Elementos Clave |
| :---- | :---- | :---- |
| **Panel de Herramientas** | Extremo Izquierdo (Vertical) | Botones para: Añadir QR, Texto, Cuadros de Color, Contenedores de Fotos. |
| **Pestañas de Diseño** | Lateral Izquierdo (Pestañas) | Plantillas, Temas, Máscaras, Cliparts, Fondos, Bordes. |
| **Lienzo Principal** | Centro | Área de trabajo (Tapa/Contratapa o Doble Página). |
| **Panel de Propiedades** | Lateral Derecho | Aparece al seleccionar un objeto. Controla fuentes, colores, tamaños y rotación. |
| **Navegador de Páginas** | Inferior (Horizontal) | Miniaturas para saltar entre páginas y botón "Añadir Páginas". |
| **Barra de Acción** | Superior Derecha | Botones de "Guardar", "Comprar" (Finalizar) y "Deshacer". |

## **2\. Flujo de Trabajo Paso a Paso**

### **Paso 1: Configuración Inicial**

1. **Selección:** Navegar a "Fotolibros" \-\> Elegir Formato (ej. 21x21 Tapa Dura).  
2. **Carga de Fotos:** Subir archivos desde la computadora o Instagram.  
3. **Selección de Tema:** Elegir una colección (ej. "Minimal") y seleccionar **"Relleno de fotos manual"** para control total.

### **Paso 2: Diseño de Tapa y Lomo (Crucial)**

* **La Tapa:** La zona derecha del lienzo central es la portada; la izquierda es la contratapa.  
* **El Lomo:** Es la franja central entre las líneas punteadas.  
  * **Acción:** Click en herramienta "Texto" \-\> Doble click para escribir \-\> En el Panel Derecho, usar el **tirador circular** sobre la caja de texto para rotar 90°.  
  * **Ajuste:** Centrar manualmente entre las líneas punteadas.

### **Paso 3: Manipulación de Elementos**

* **Fotos:** Arrastrar desde la galería izquierda al lienzo.  
  * *Herramienta Mano:* Aparece al hacer click en una foto; permite mover la imagen dentro de su marco.  
  * *Zoom:* Control deslizante en el panel derecho para ampliar detalles de la foto.  
* **Alineación:** Mantener presionada la tecla **SHIFT** mientras se mueve un objeto para activar las **guías de centrado automáticas**.  
* **QR Codes:** Seleccionar herramienta "Añadir QR" \-\> Pegar URL (YouTube/Instagram) \-\> El sistema genera el código imprimible.

## **3\. Guía Visual de Herramientas Específicas**

### **Gestión de Fondos y Bordes**

1. **Fondos:** Pestaña "Fondos" \-\> Seleccionar color o galería. Se puede aplicar a "Página izquierda", "Página derecha" o "Todo el libro".  
   * *Tip:* Usar el **Gotero** para copiar un color exacto de una de las fotografías.  
2. **Bordes:** Pestaña "Bordes". Seleccionar grosor (px) y color (blanco es el estándar profesional).

### **Uso de Plantillas (Layouts)**

Para diseños rápidos con múltiples fotos:

1. Ir a pestaña "Plantillas".  
2. Filtrar por número de fotos (ej. "4 fotos").  
3. Arrastrar la plantilla elegida a la página deseada.

## **4\. Instrucciones para Replicar la Imagen Adjunta**

Basado en el análisis de la imagen proporcionada (image\_f635cf.png), estas son las instrucciones precisas para que el Agente IA replique ese estilo:

1. **Layout de Foto Principal:** Crear un contenedor de foto que ocupe el 70% superior de la página derecha.  
2. **Adornos de Fondo:** \* Ir a la pestaña **Fondos** o **Cliparts**.  
   * Seleccionar un patrón de líneas o textura suave (similar al estilo "Stripes" mencionado en los tutoriales).  
3. **Cuadros de Texto con Estilo:**  
   * Insertar un cuadro de texto principal debajo de la foto.  
   * **Fuente:** Serif o Script elegante (similar a "Great Vibes" o "Lora").  
   * **Color de fondo de texto:** Si la imagen muestra un bloque de color tras el texto, usar la herramienta "Añadir plano de color", enviarlo al fondo (botón derecho \-\> Capas) y colocar el texto encima.  
4. **Distribución Visual:** \* La imagen sugiere un diseño **limpio (Minimal)**.  
   * Dejar márgenes generosos (espacio en blanco) en los bordes para evitar cortes en la encuadernación.  
5. **Detalle Especial (QR/Lomo):** Si la imagen muestra un código QR, colocarlo en una esquina inferior con un tamaño no menor a 2x2 cm para asegurar la lectura.

## **5\. Reglas de Oro para el Agente IA (Claude/Browser Agent)**

* **Seguridad del Lomo:** Nunca colocar caras o textos importantes justo en el pliegue central (lomo) de las páginas interiores, ya que la costura "comerá" parte de la imagen.  
* **Guardado:** Ejecutar la acción de "Guardar" (botón superior) cada 5 minutos o tras finalizar cada doble página.  
* **Doble Página:** Para una foto que ocupe ambas páginas, estirar el contenedor de extremo a extremo y desplazar el motivo principal (personas) hacia un lado para que no queden cortados por la mitad.