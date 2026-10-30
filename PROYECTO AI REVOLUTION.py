import tkinter as tk
import ast
from tkinter import messagebox
from tkinter import simpledialog
import random
import copy

# ------------
# Constantes
# ------------

ANCHO_MAPA = 800
ALTO_MAPA = 400


# ---------------------------------------
# Commons
# ---------------------------------------

# Da formato a un número para mostrarlo
# E: número entero o decimal
# S: texto con separadores de miles y sin decimales
# R: el valor debe ser numérico
def formatear_numero(numero):
    return f"{numero:,.0f}"


# Convierte grados, minutos y segundos a grados decimales para que sea más fácil leer los datos
# E: grados, minutos y segundos
# S: coordenada en grados decimales
# R: minutos y segundos entre 0 y 59
def convertir_a_decimal(grados, minutos, segundos):
    minutos_en_grados = minutos / 60
    segundos_en_grados = segundos / 3600

    decimal = abs(grados) + minutos_en_grados + segundos_en_grados

    if grados < 0:
        decimal = -decimal

    return decimal


# Convierte una longitud decimal a una posición horizontal.
# E: longitud en grados decimales
# S: posición x en el Canvas
# R: longitud entre -180 y 180
def longitud_a_x(longitud):
    x = (longitud + 180) * ANCHO_MAPA / 360
    return x


# Convierte una latitud decimal a una posición vertical.
# E: latitud en grados decimales.
# S: posición y en el Canvas.
# R: latitud entre -90 y 90.
def latitud_a_y(latitud):
    y = (90 - latitud) * ALTO_MAPA / 180
    return y

# Calcula el área de un territorio con dos esquinas opuestas
# E: longitud y latitud de ambos puntos, ya en grados decimales
# S: área en kilómetros cuadrados
# R: coordenadas válidas. Cada grado representa 600 km
def calcular_area(longitud1, latitud1, longitud2, latitud2):
    diferencia_longitud = abs(longitud2 - longitud1)
    diferencia_latitud = abs(latitud2 - latitud1)

    ancho = diferencia_longitud * 600
    alto = diferencia_latitud * 600

    area = ancho * alto

    return area

# Convierte un punto del mapa a una posición en el canvas
# E: punto con formato (LONGITUD) (LATITUD) [[grados, minutos, segundos], [grados, minutos, segundos]].
# S: lista [x, y] con la posición en píxeles
# R: las coordenadas deben ser válidas

def punto_a_canvas(punto):
    longitud = punto[0]
    latitud = punto[1]

    longitud_decimal = convertir_a_decimal(
        longitud[0], longitud[1], longitud[2]
    )

    latitud_decimal = convertir_a_decimal(
        latitud[0], latitud[1], latitud[2]
    )

    x = longitud_a_x(longitud_decimal)
    y = latitud_a_y(latitud_decimal)

    return [x, y]

# Pide un entero y muestra los errores en español
# E: título, mensaje, valor mínimo y valor máximo
# S: entero válido o None si se cancela
# R: mínimo y máximo deben ser enteros y mínimo <= máximo
def pedir_entero(titulo, mensaje, minimo, maximo):
    while True:
        texto = simpledialog.askstring(
            titulo,
            mensaje,
            parent=ventana
        )

        if texto is None:
            return None

        try:
            numero = int(texto)
        except ValueError:
            messagebox.showerror(
                "Dato inválido",
                "Debe ingresar un número entero.",
                parent=ventana
            )
            continue

        if numero < minimo:
            messagebox.showerror(
                "Número demasiado pequeño",
                "El valor mínimo permitido es " + str(minimo) + ".",
                parent=ventana
            )
            continue

        if numero > maximo:
            messagebox.showerror(
                "Número demasiado grande",
                "El valor máximo permitido es " + str(maximo) + ".",
                parent=ventana
            )
            continue

        return numero

# Calcula el área de un territorio a partir de sus dos puntos
# E: lista con dos puntos en grados, minutos y segundos
# S: área del territorio en kilómetros cuadrados
# R: los puntos deben tener coordenadas válidas
def area_territorio(puntos):
    limites = obtener_limites(puntos)

    izquierda = limites[0]
    derecha = limites[1]
    abajo = limites[2]
    arriba = limites[3]

    area = calcular_area(izquierda, abajo, derecha, arriba)

    return area

    

    # Comprueba si una posición está dentro de un territorio
# E: longitud y latitud decimales; límites del territorio
# S: True si está dentro o en el borde y False si está fuera
# R: coordenadas válidas y límites en el orden
#    [izquierda, derecha, abajo, arriba]
def punto_en_territorio(longitud, latitud, limites):
    izquierda = limites[0]
    derecha = limites[1]
    abajo = limites[2]
    arriba = limites[3]

    if longitud < izquierda or longitud > derecha:
        return False

    if latitud < abajo or latitud > arriba:
        return False

    return True

# ---------------------------------------
# Archivos y validaciones
# ---------------------------------------


# Lee cualquier archivo
# E: ruta del archivo
# S: datos leídos o None si pasa un error de lectura

def leer_archivo(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()

        mapa = ast.literal_eval(contenido)
        return mapa

    except FileNotFoundError:
        messagebox.showerror(
            "Error de archivo",
            "No se encontró el archivo: " + ruta,
            parent=ventana
        )

    except (SyntaxError, ValueError):
        messagebox.showerror(
            "Error de archivo",
            "El archivo mapa.txt está mal escrito.",
            parent=ventana
        )

    except UnicodeError:
        messagebox.showerror(
            "Error de archivo",
            "No se pudo leer el texto de mapa.txt. Guarde el archivo con codificación UTF-8.",
            parent=ventana
        )

    except OSError:
        messagebox.showerror(
            "Error de archivo",
            "No se pudo abrir o leer mapa.txt.",
            parent=ventana
        )

    return None


# Comprueba si una coordenada es válida.
# E: lista [grados, minutos, segundos] y límite de grados.
# S: True si es válida; False si no.
# R: límite de 180 para longitud o 90 para latitud.
def validar_coordenada(coordenada, limite):
    if not isinstance(coordenada, list):
        return False

    if len(coordenada) != 3:
        return False

    for valor in coordenada:
        if type(valor) != int:
            return False

    grados = coordenada[0]
    minutos = coordenada[1]
    segundos = coordenada[2]

    if minutos < 0 or minutos > 59:
        return False

    if segundos < 0 or segundos > 59:
        return False

    decimal = convertir_a_decimal(grados, minutos, segundos)

    if abs(decimal) > limite:
        return False

    return True
# Comprueba si un punto tiene longitud y latitud válidas
# E: punto con formato [longitud, latitud]
# S: True si es válido y False si no
# R: cada coordenada debe contener grados, minutos y segundos enteros

def validar_punto(punto):
    if not isinstance(punto, list):
        return False

    if len(punto) != 2:
        return False

    longitud = punto[0]
    latitud = punto[1]

    if not validar_coordenada(longitud, 180):
        return False

    if not validar_coordenada(latitud, 90):
        return False

    return True

# Revisa las coordenadas de todos los territorios del mapa
# E: mapa con países, estados y territorios
# S: mensaje de error o texto vacío si no encuentra errores
# R: el mapa debe tener la estructura de países, estados y territorios

def revisar_coordenadas_mapa(mapa):
    for pais in mapa:
        for estado in pais[1]:
            for territorio in estado[1]:
                nombre = territorio[0]
                puntos = territorio[1]

                if not isinstance(puntos, list):
                    return "Los puntos no son una lista: " + nombre

                if len(puntos) != 2:
                    return "El territorio debe tener dos puntos: " + nombre

                for punto in puntos:
                    if not validar_punto(punto):
                        return (
                            "Coordenadas inválidas en: "
                            + pais[0] + " / "
                            + estado[0] + " / "
                            + nombre
                        )

    return ""

# Reune los nombres y límites de todos los territorios
# E: mapa con países, estados y territorios
# S: lista de registros [país, estado, territorio, límites]

def reunir_territorios(mapa):
    lista_territorios = []

    for pais in mapa:
        for estado in pais[1]:
            for territorio in estado[1]:
                limites = obtener_limites(territorio[1])

                registro = [
                    pais[0],
                    estado[0],
                    territorio[0],
                    limites
                                ]
                lista_territorios.append(registro)
    return lista_territorios




#|||||TRASLAPES|||||||

# Obtiene los límites de un territorio
# E: lista con las dos esquinas del territorio
# S: lista [izquierda, derecha, abajo, arriba] en grados decimales
# R: los dos puntos deben tener coordenadas válidas
def obtener_limites(puntos):
    punto1 = puntos[0]
    punto2 = puntos[1]

    longitud1 = punto1[0]
    latitud1 = punto1[1]

    longitud2 = punto2[0]
    latitud2 = punto2[1]

    lon1 = convertir_a_decimal(
        longitud1[0], longitud1[1], longitud1[2]
    )
    lat1 = convertir_a_decimal(
        latitud1[0], latitud1[1], latitud1[2]
    )

    lon2 = convertir_a_decimal(
        longitud2[0], longitud2[1], longitud2[2]
    )
    lat2 = convertir_a_decimal(
        latitud2[0], latitud2[1], latitud2[2]
    )

    izquierda = min(lon1, lon2)
    derecha = max(lon1, lon2)
    abajo = min(lat1, lat2)
    arriba = max(lat1, lat2)

    return [izquierda, derecha, abajo, arriba]


# Comprueba si dos territorios comparten una zona de área
# E: límites de ambos territorios: [izquierda, derecha, abajo, arriba]
# S: True si se traslapan y False si no
# R: límites válidos de rectángulos con área mayor a cero


def hay_traslape(limites1, limites2):
    izquierda1 = limites1[0]
    derecha1 = limites1[1]
    abajo1 = limites1[2]
    arriba1 = limites1[3]

    izquierda2 = limites2[0]
    derecha2 = limites2[1]
    abajo2 = limites2[2]
    arriba2 = limites2[3]

    if derecha1 <= izquierda2:
        return False

    if izquierda1 >= derecha2:
        return False

    if arriba1 <= abajo2:
        return False

    if abajo1 >= arriba2:
        return False

    return True

# Busca el primer traslape entre territorios del mapa
# E: mapa con países, estados y territorios.
# S: mensaje del primer traslape o texto vacío si no encuentra.
# R: No hay
def revisar_traslapes(mapa):
    territorios = reunir_territorios(mapa)
    cantidad = len(territorios)

    for i in range(cantidad):
        for j in range(i + 1, cantidad):
            territorio1 = territorios[i]
            territorio2 = territorios[j]

            limites1 = territorio1[3]
            limites2 = territorio2[3]

            if hay_traslape(limites1, limites2):
                nombre1 = (
                    territorio1[0] + ' / '
                    + territorio1[1] + ' / '
                    + territorio1[2]
                )

                nombre2 = (
                    territorio2[0] + ' / '
                    + territorio2[1] + ' / '
                    + territorio2[2]
                )

                return nombre1 + ' se traslapa con ' + nombre2

    return ''

# Agrega un disparo al archivo de bitacora
# E: registro con los datos del disparo
# S: escribe el registro en bitácora.txt
def guardar_disparo_archivo(registro):
    try:
        with open("bitácora.txt", "a", encoding="utf-8") as file:
            file.write(str(registro) + "\n")

    except OSError:
        messagebox.showerror(
            "Error de archivo",
            "No se pudo guardar el disparo en bitácora.txt.",
            parent=ventana
        )
#||||||||||||||||||||||||||||||||||||||||||||||||||||||


# ---------------------------------------
# Funciones de la simulación
# ---------------------------------------

# Busca los tipos de misiles disponibles asociados a una clave.
# E: lista de países con misiles y clave de dos dígitos como texto.
# S: lista de registros [país, tipo de misil, disponibles].
# R: los datos deben seguir el formato de misiles.txt.
def buscar_misiles(misiles, clave):
    encontrados = []

    for pais in misiles:
        lista_misiles = pais[3]

        for misil in lista_misiles:
            if misil[4] == clave and misil[3] > 0:
                registro = [pais[0], misil[0], misil[3]]
                encontrados.append(registro)

    return encontrados

# Busca los territorios que contienen un punto de destino.
# E: mapa y destino con formato [longitud, latitud] en grados, minutos y segundos
# S: lista de coincidencias [país, estado, territorio]
# R: mapa y destino con coordenadas válidas
def buscar_territorios_destino(mapa, destino):
    longitud = destino[0]
    latitud = destino[1]

    lon = convertir_a_decimal(
        longitud[0], longitud[1], longitud[2]
    )

    lat = convertir_a_decimal(
        latitud[0], latitud[1], latitud[2]
    )

    encontrados = []

    for pais in mapa:
        for estado in pais[1]:
            for territorio in estado[1]:
                limites = obtener_limites(territorio[1])

                if punto_en_territorio(lon, lat, limites):
                    registro = [
                        pais[0],
                        estado[0],
                        territorio[0],
                        territorio
                    ]
                    encontrados.append(registro)

    return encontrados
# Crea los registros de vida de los territorios
# E: mapa con países, estados y territorios
# S: lista de registros con nombres, área inicial y área viva
# R: el mapa debe estar validado


# Crea los registros de vida de los territorios
# E: mapa con países estados y territorios
# S: registros con nombres áreas e identificador

def crear_vida_territorios(mapa):
    registros = []
    identificador = 1

    for pais in mapa:
        for estado in pais[1]:
            for territorio in estado[1]:
                area = area_territorio(territorio[1])

                registro = [
                    pais[0],
                    estado[0],
                    territorio[0],
                    area,
                    area,
                    identificador,
                    territorio
                ]

                registros.append(registro)
                identificador += 1

    return registros

# Pide una longitud o latitud mediante ventanas.
# E: nombre de la coordenada y límite de grados.
# S: lista [grados, minutos, segundos] o None si se cancela.
# R: límite de 180 para longitud o 90 para latitud.

def pedir_coordenada(nombre, limite):
    grados = pedir_entero(
    nombre,
    "Ingrese los grados del destino al que desea disparar:",-limite,limite)

    if grados is None:
        return None

    minutos = pedir_entero(
        nombre,
        "Ingrese los minutos del destino al que desea disparar:",0,59)
    

    if minutos is None:
        return None

    segundos = pedir_entero(
        nombre,
        "Ingrese los segundos del destino al que desea disparar:",0,59)

    if segundos is None:
        return None

    coordenada = [grados, minutos, segundos]

    if not validar_coordenada(coordenada, limite):
        messagebox.showerror(
            "Coordenada inválida",
            "La coordenada completa supera el límite permitido.",
            parent=ventana
        )
        return None

    return coordenada

def seleccionar_clave_manual():
    clave = simpledialog.askstring(
        "IA manual",
        "Ingrese una clave de dos dígitos que sean de 00 a 99:",
        parent=ventana
    )

    if clave is None:
        return

    if len(clave) != 2 or not clave.isdecimal():
        messagebox.showerror(
            "Clave inválida",
            "Tiene que escribir dos dígitos",
            parent=ventana
        )
        return
    ejecutar_disparos(clave, "Manual")
    


# Ejecuta los disparos asociados a una clave
# E: clave de dos dígitos y modo de selección
# S: actualiza vida, inventario, mapa e historial

def ejecutar_disparos(clave, modo):

    if verificar_victoria(mapa_original, mapa_muertos):
        messagebox.showinfo(
            "Simulación terminada",
            "La IA ya destruyó más del 50 % de los territorios.",
            parent=ventana
        )
        return
    encontrados = buscar_misiles(misiles, clave)

    if encontrados == []:
        messagebox.showinfo(
            "Misiles",
            "No hay misiles disponibles con esa clave.",
            parent=ventana
        )
        return

    mensaje = ""

    for registro in encontrados:
        mensaje += (
            registro[0] + " / "
            + registro[1] + " / Disponibles: "
            + str(registro[2]) + "\n"
        )

    messagebox.showinfo("¡La IA ha encontrado la clave!", mensaje, parent=ventana)

    for registro in encontrados:
        pais = registro[0]
        tipo = registro[1]
        disponibles = registro[2]

        cantidad = pedir_entero(
            "Cantidad de misiles",
            pais + " / " + tipo
            + "\nDisponibles: " + str(disponibles)
            + "\n¿Cuántos desea disparar? (0 para omitir)",
            0,
            disponibles
        )

        if cantidad is None:
            return

        if cantidad == 0:
            continue
        longitud = pedir_coordenada("Longitud del destino", 180)

        if longitud is None:
            return

        latitud = pedir_coordenada("Latitud del destino", 90)

        if latitud is None:
            return

        destino = [longitud, latitud]

        # Aqui se muestra el destino para comprobar lo que se ingresó
        territorios = buscar_territorios_destino(mapa, destino)

        if territorios == []:
            descontar_misiles(misiles, pais, tipo, cantidad)
            dibujar_disparo(destino)
            registrar_disparo(
                historial_disparos,
                modo,
                clave,
                pais,
                tipo,
                cantidad,
                destino,
                [],
                None
            )

            messagebox.showinfo(
                "Disparo fallido",
                "El disparo no alcanzó ningún territorio."
                "\nMisiles utilizados: " + str(cantidad),
                parent=ventana
            )


        elif len(territorios) == 1:
            encontrado = territorios[0]
            territorio = encontrado[:3]
            territorio_mapa = encontrado[3]

            registro = buscar_vida_por_territorio(
                vida_territorios, territorio_mapa
            )
            

            if registro is None:
                messagebox.showerror(
                    "Error",
                    "No se encontró el registro de vida del territorio.",
                    parent=ventana
                )
                return

            misil = buscar_registro_misil(misiles, pais, tipo)

            if misil is None:
                messagebox.showerror(
                    "Error",
                    "No se encontró el misil seleccionado.",
                    parent=ventana
                )
                return

            capacidad = misil[1]
            dano_total = capacidad * cantidad

            dano_real = aplicar_dano(registro, dano_total)

            murio = mover_territorio_muerto(
                mapa, mapa_muertos, registro
            )

            if murio:
                etiqueta = "territorio_" + str(registro[5])
                canvas.delete(etiqueta)

            descontar_misiles(misiles, pais, tipo, cantidad)
            dibujar_disparo(destino)
            registrar_disparo(
                historial_disparos,
                modo,
                clave,
                pais,
                tipo,
                cantidad,
                destino,
                territorio,
                registro[5]
            )

            area_inicial = registro[3]
            area_viva = registro[4]
            if area_inicial > 0:
                porcentaje_vida = area_viva / area_inicial * 100
            else:
                porcentaje_vida = 0

            messagebox.showinfo(
                "Resultado",
                "\nDisparo realizado con éxito."
                "\nPaís: " + territorio[0] +
                "\nEstado: " + territorio[1] +
                "\nTerritorio: " + territorio[2] +
                "\nMisiles utilizados: " + str(cantidad) +
                "\nÁrea destruida: " + formatear_numero(dano_real) + " km²" +
                "\nÁrea inicial: " + formatear_numero(area_inicial) + " km²" +
                "\nÁrea viva: " + formatear_numero(area_viva) + " km²" +
                "\nVida restante: " + str(round(porcentaje_vida, 2)) + "%",
                parent=ventana
            )
            if verificar_victoria(mapa_original, mapa_muertos):
                messagebox.showinfo(
                    "Victoria de la IA",
                    "La IA destruyó más del 50 % de los territorios."
                    "\nLa simulación ha terminado.",
                    parent=ventana
                )

                boton_manual.config(state="disabled")
                boton_aleatorio.config(state="disabled")
                return    

        else:
            messagebox.showinfo(
                "Destino compartido",
                "El punto pertenece a varios territorios."
                "\nNo se realizó el disparo ni se descontaron misiles.",
                parent=ventana
            )

# Registra un disparo y su resultado en la lista y el archivo.
# E: historial, modo, clave, país de origen, tipo, cantidad,
#    destino, territorio alcanzado e identificador
# S: agrega el registro al historial y a bitácora.txt
# R: territorio debe ser [] si el disparo no acertó
def registrar_disparo(historial, modo, clave, pais_origen,
                      tipo, cantidad, destino, territorio,
                      identificador):
    if territorio == []:
        resultado = "Falló"
    else:
        resultado = "Acertó"

    registro = [
        modo,
        clave,
        pais_origen,
        tipo,
        cantidad,
        destino,
        territorio,
        identificador,
        resultado
    ]

    historial.append(registro)
    guardar_disparo_archivo(registro)

# Busca el registro de vida de un territorio
# E: lista de registros y destino [país, estado, territorio]
# S: registro de vida encontrado o None si no existe
# R: los registros deben tener el formato establecido
def buscar_vida_territorio(registros, destino):
    for registro in registros:
        if (registro[0] == destino[0] and
            registro[1] == destino[1] and
            registro[2] == destino[2]):
            return registro

    return None

# Busca el registro de vida del territorio indicado
# E: registros de vida y territorio completo del mapa
# S: registro encontrado o None si no existe
# R: el registro tiene que guardar el territorio en la posición 6
def buscar_vida_por_territorio(registros, territorio):
    for registro in registros:
        if registro[6] is territorio:
            return registro

    return None

# Permite elegir uno de varios registros de vida
# E: lista de registros que coinciden con la búsqueda
# S: registro elegido o None si no hay resultados o se cancela

def elegir_registro_territorio(coincidencias):
    if coincidencias == []:
        messagebox.showerror(
            "Territorio no encontrado",
            "No se encontraron territorios con esos datos.",
            parent=ventana
        )
        return None

    if len(coincidencias) == 1:
        return coincidencias[0]

    mensaje = "Hay varios territorios con ese nombre:\n\n"

    for posicion in range(len(coincidencias)):
        registro = coincidencias[posicion]
        puntos = registro[6][1]

        mensaje += (
            str(posicion + 1) + ". ID: " + str(registro[5]) +
            "\nPuntos: " + str(puntos) + "\n\n"
        )

    opcion = pedir_entero(
        "Seleccionar territorio",
        mensaje + "Ingrese el número de la opción:",
        1,
        len(coincidencias)
    )

    if opcion is None:
        return None

    return coincidencias[opcion - 1]


# Aplica daño al área viva de un territorio
# E: registro de vida y daño en kilómetros cuadrados
# S: cantidad de kilómetros cuadrados destruidos
# R: el daño debe ser mayor o igual a cero
def aplicar_dano(registro, dano):
    area_viva = registro[4]

    if dano > area_viva:
        dano = area_viva

    registro[4] = area_viva - dano

    return dano

# Busca un tipo de misil dentro de un país
# E: lista de misiles, nombre del país y nombre del misil
# S: registro del misil o None si no se encuentra
# R: la lista debe tener el formato establecido
def buscar_registro_misil(misiles, nombre_pais, nombre_misil):
    for pais in misiles:
        if pais[0] == nombre_pais:
            for misil in pais[3]:
                if misil[0] == nombre_misil:
                    return misil

    return None

# Descuenta los misiles utilizados del inventario
# E: lista de misiles, país, tipo y cantidad disparada
# S: actualiza los disponibles del tipo y del país

def descontar_misiles(misiles, nombre_pais, nombre_misil, cantidad):
    for pais in misiles:
        if pais[0] == nombre_pais:
            for misil in pais[3]:
                if misil[0] == nombre_misil:
                    misil[3] = misil[3] - cantidad
                    pais[2] = pais[2] - cantidad
                    return

# Dibuja una marca en el destino de un disparo
# E: destino [longitud, latitud] en grados, minutos y segundos
# S: una cruz roja en el Canvas

def dibujar_disparo(destino):
    posicion = punto_a_canvas(destino)

    x = posicion[0]
    y = posicion[1]

    canvas.create_line(
        x - 4, y - 4,
        x + 4, y + 4,
        fill="red",
        width=10
    )

    canvas.create_line(
        x - 4, y + 4,
        x + 4, y - 4,
        fill="red",
        width=10
    )


def seleccionar_clave_aleatoria():
    numero = random.randint(0, 99)
    clave = str(numero)

    if numero < 10:
        clave = "0" + clave

    messagebox.showinfo(
        "IA aleatoria",
        "La clave generada es: " + clave,
        parent=ventana
    )

    ejecutar_disparos(clave, "Aleatorio")


# Esto busca un estado dentro de un país
# E: mapa, nombre del país y nombre del estado
# S: registro del estado encontrado o None si no existe
# R: el mapa debe tener la estructura establecida
def buscar_estado(mapa, nombre_pais, nombre_estado):
    for pais in mapa:
        if pais[0] == nombre_pais:
            for estado in pais[1]:
                if estado[0] == nombre_estado:
                    return estado

    return None

# Busca un territorio dentro de un estado
# E: registro del estado y nombre del territorio
# S: registro del territorio encontrado o None si no existe

def buscar_territorio(estado, nombre_territorio):
    for territorio in estado[1]:
        if territorio[0] == nombre_territorio:
            return territorio

    return None

# Traslada un territorio a un estado de otro país
# E: mapa, registros de vida y nombres de origen y destino
# S: texto vacío si se trasladó o un mensaje de error
def trasladar_territorio(mapa, registros, pais_origen,
                        estado_origen, nombre_territorio,
                        pais_destino, estado_destino):
    if pais_origen == pais_destino:
        return "El país de destino debe ser diferente al de origen."

    origen = buscar_estado(mapa, pais_origen, estado_origen)
    destino = buscar_estado(mapa, pais_destino, estado_destino)

    if origen is None:
        return "No se encontro el país o estado de origen"

    if destino is None:
        return "No se encontró el país o estado de destino."

    coincidencias = []

    for territorio_actual in origen[1]:
        if territorio_actual[0] == nombre_territorio:
            registro = buscar_vida_por_territorio(
                registros, territorio_actual
            )

            if registro is not None:
                coincidencias.append(registro)

    if coincidencias == []:
        return "No se encontró el territorio en el estado de origen."

    elegido = elegir_registro_territorio(coincidencias)

    if elegido is None:
        return "Traslado cancelado."

    territorio = elegido[6]
    repetido = buscar_territorio(destino, nombre_territorio)

    if repetido is not None:
        return "Ya existe un territorio con ese nombre en el estado de destino."

    vida = buscar_vida_por_territorio(registros, territorio)

    if vida is None:
        return "No se encontró el registro de vida del territorio."

    origen[1].remove(territorio)
    destino[1].append(territorio)

    vida[0] = pais_destino
    vida[1] = estado_destino
    dibujar_nombre_pais(vida)

    return ""
# Solicita los datos para trasladar un territorio.
# E: nombres del país, estado y territorio de origen y del país y estado de destino
# S: realiza el traslado o muestra un mensaje de error
# R: mapa y registros de vida disponibles
def solicitar_traslado():
    pais_origen = simpledialog.askstring(
        "Trasladar territorio",
        "Ingrese el país de origen:",
        parent=ventana
    )
    if pais_origen is None:
        return

    estado_origen = simpledialog.askstring(
        "Trasladar territorio",
        "Ingrese el estado de origen:",
        parent=ventana
    )
    if estado_origen is None:
        return

    nombre_territorio = simpledialog.askstring(
        "Trasladar territorio",
        "Ingrese el nombre del territorio:",
        parent=ventana
    )
    if nombre_territorio is None:
        return

    pais_destino = simpledialog.askstring(
        "Trasladar territorio",
        "Ingrese el país de destino:",
        parent=ventana
    )
    if pais_destino is None:
        return

    estado_destino = simpledialog.askstring(
        "Trasladar territorio",
        "Ingrese el estado de destino:",
        parent=ventana
    )
    if estado_destino is None:
        return

    error = trasladar_territorio(
        mapa,
        vida_territorios,
        pais_origen,
        estado_origen,
        nombre_territorio,
        pais_destino,
        estado_destino
    )

    if error != "":
        messagebox.showerror(
            "No se pudo trasladar",
            error,
            parent=ventana
        )
        return

    messagebox.showinfo(
        "Traslado hecho con éxito",
        nombre_territorio + " ahora pertenece a " +
        pais_destino + " / " + estado_destino + ".",
        parent=ventana
    )

# Guarda un territorio en el mapa de territorios muertos
# E: mapa de muertos, nombres del país y estado, y territorio
# S: agrega el territorio bajo su país y estado

def agregar_territorio_muerto(muertos, nombre_pais,
                             nombre_estado, territorio):
    pais_encontrado = None

    for pais in muertos:
        if pais[0] == nombre_pais:
            pais_encontrado = pais
            break

    if pais_encontrado is None:
        pais_encontrado = [nombre_pais, []]
        muertos.append(pais_encontrado)

    estado_encontrado = buscar_estado(
        muertos, nombre_pais, nombre_estado
    )

    if estado_encontrado is None:
        estado_encontrado = [nombre_estado, []]
        pais_encontrado[1].append(estado_encontrado)

    estado_encontrado[1].append(territorio)


# Pasa un territorio destruido del mapa a la lista de muertos.
# E: mapa, lista de muertos y registro de vida del territorio
# S: True si se trasladó; False si no se pudo trasladar
# el registro tiene que guardar el territorio en la posición 6
def mover_territorio_muerto(mapa, muertos, registro):
    if registro[4] > 0:
        return False

    pais = registro[0]
    estado = registro[1]
    territorio = registro[6]

    estado_origen = buscar_estado(mapa, pais, estado)

    if estado_origen is None:
        return False

    territorios = estado_origen[1]

    for posicion in range(len(territorios)):
        if territorios[posicion] is territorio:
            agregar_territorio_muerto(
                muertos, pais, estado, territorio
            )

            territorios.pop(posicion)
            return True

    return False


# Cuenta todos los territorios de un mapa
# E: mapa organizado por países, estados y territorios
# S: cantidad total de territorios
# R: el mapa debe tener la estructura establecida
def contar_territorios(mapa):
    cantidad = 0

    for pais in mapa:
        for estado in pais[1]:
            cantidad += len(estado[1])

    return cantidad

def verificar_victoria(mapa_original, mapa_muertos):
    total = contar_territorios(mapa_original)
    muertos = contar_territorios(mapa_muertos)

    return muertos > total / 2

# Muestra quién gana según el estado actual de la simulación
# E: utiliza el mapa original y la lista de territorios muertos
# S: mensaje con el ganador actual

def mostrar_ganador():
    victoria_ia = verificar_victoria(mapa_original, mapa_muertos)

    if victoria_ia:
        mensaje = "La IA gana! destruyó más del 50 % de los territorios."
    else:
        mensaje = (
            "La IA va perdiendo, no ha destruido "
            "más del 50 % de los territorios."
        )

    messagebox.showinfo(
        "Ganador actual",
        mensaje,
        parent=ventana
    )


# ---------------------------------------
# Consultas
# ---------------------------------------

# Calcula las áreas y el porcentaje de vida de un país.
# E: registros de vida y nombre del país
# S: [área inicial, área viva, área destruida, porcentaje de vida]
# R: el país debe existir
def consultar_vida_pais(registros, nombre_pais):
    area_inicial = 0
    area_viva = 0

    for registro in registros:
        if registro[0] == nombre_pais:
            area_inicial += registro[3]
            area_viva += registro[4]

    area_destruida = area_inicial - area_viva

    if area_inicial > 0:
        porcentaje_vida = area_viva / area_inicial * 100
    else:
        porcentaje_vida = 0

    return [
        area_inicial,
        area_viva,
        area_destruida,
        porcentaje_vida
    ]

# Muestra las áreas y el porcentaje de vida de cada país
# E: utiliza mapa y vida_territorios
# S: ventana con los resultados por país
# R: el mapa debe estar cargado y validado
def mostrar_vida_paises():
    mensaje = ""

    for pais in mapa:
        datos = consultar_vida_pais(vida_territorios, pais[0])

        mensaje += (
            "País: " + pais[0] +
            "\nÁrea inicial: " + formatear_numero(datos[0]) + " km²" +
            "\nÁrea viva: " + formatear_numero(datos[1]) + " km²" +
            "\nÁrea destruida: " + formatear_numero(datos[2]) + " km²" +
            "\nVida restante: " + str(round(datos[3], 2)) + "%" +
            "\n\n"
        )

    if mensaje == "":
        mensaje = "No hay países para mostrar."

    messagebox.showinfo(
        "Vida de los países",
        mensaje,
        parent=ventana
    )

# Calcula las áreas y el porcentaje de vida de un estado
# E: registros de vida, nombre del país y nombre del estado
# S: [área inicial, área viva, área destruida, porcentaje de vida]
# R: el estado debe existir dentro del país indicado
def consultar_vida_estado(registros, nombre_pais, nombre_estado):
    area_inicial = 0
    area_viva = 0

    for registro in registros:
        if (registro[0] == nombre_pais and
            registro[1] == nombre_estado):
            area_inicial += registro[3]
            area_viva += registro[4]

    area_destruida = area_inicial - area_viva

    if area_inicial > 0:
        porcentaje_vida = area_viva / area_inicial * 100
    else:
        porcentaje_vida = 0

    return [
        area_inicial,
        area_viva,
        area_destruida,
        porcentaje_vida
    ]

# Aqui muestra las áreas y el porcentaje de vida de cada estado
# E: utiliza mapa y vida_territorios
# S: ventana con los resultados por país y estado

def mostrar_vida_estados():
    mensaje = ""

    for pais in mapa:
        for estado in pais[1]:
            datos = consultar_vida_estado(
                vida_territorios, pais[0], estado[0]
            )

            mensaje += (
                "País: " + pais[0] +
                "\nEstado: " + estado[0] +
                "\nÁrea inicial: " + formatear_numero(datos[0]) + " km²" +
                "\nÁrea viva: " + formatear_numero(datos[1]) + " km²" +
                "\nÁrea destruida: " + formatear_numero(datos[2]) + " km²" +
                "\nVida restante: " + str(round(datos[3], 2)) + "%" +
                "\n\n"
            )

    if mensaje == "":
        mensaje = "No hay estados para mostrar."

    messagebox.showinfo(
        "Vida de los estados",
        mensaje,
        parent=ventana
    )
# Muestra las áreas y el porcentaje de vida de cada territorio.
# E: utiliza la lista vida_territorios.
# S: ventana con los resultados de los territorios.
# R: el mapa debe estar cargado y validado.
def mostrar_vida_territorios():
    mensaje = ""

    for registro in vida_territorios:
        area_inicial = registro[3]
        area_viva = registro[4]
        area_destruida = area_inicial - area_viva

        if area_inicial > 0:
            porcentaje = area_viva / area_inicial * 100
        else:
            porcentaje = 0

        mensaje += (
            "País: " + registro[0] +
            "\nEstado: " + registro[1] +
            "\nTerritorio: " + registro[2] +
            "\nÁrea inicial: " + formatear_numero(area_inicial) + " km²" +
            "\nÁrea viva: " + formatear_numero(area_viva) + " km²" +
            "\nÁrea destruida: " + formatear_numero(area_destruida) + " km²" +
            "\nVida restante: " + str(round(porcentaje, 2)) + "%" +
            "\n\n"
        )

    if mensaje == "":
        mensaje = "No hay territorios para mostrar."

    ventana_consulta = tk.Toplevel(ventana)
    ventana_consulta.title("Vida de los territorios")
    ventana_consulta.geometry("600x450")

    texto = tk.Text(ventana_consulta, wrap="word")
    barra = tk.Scrollbar(ventana_consulta, command=texto.yview)
    texto.config(yscrollcommand=barra.set)

    barra.pack(side="right", fill="y")
    texto.pack(side="left", fill="both", expand=True)

    texto.insert("1.0", mensaje)
    texto.config(state="disabled")



# Obtiene el área inicial de un registro del ranking
# E: registro [nombre del país, área inicial]
# S: área inicial del país
def obtener_area_ranking(registro):
    return registro[1]


# Ordena los países por su área inicial, de mayor a menor
# E: mapa y registros de vida
# S: lista ordenada de registros [país, área inicial]

def ranking_extension_paises(mapa, registros):
    ranking = []

    for pais in mapa:
        datos = consultar_vida_pais(registros, pais[0])

        registro = [pais[0], datos[0]]
        ranking.append(registro)

    ranking.sort(key=obtener_area_ranking, reverse=True)

    return ranking

# Obtiene el porcentaje de vida de un registro del ranking
# E: registro [nombre del país, porcentaje de vida]
# S: porcentaje de vida.
def obtener_porcentaje_ranking(registro):
    return registro[1]


# Ordena los países por porcentaje de vida, de mayor a menor.
# E: mapa y registros de vida.
# S: lista ordenada [país, porcentaje de vida]

def ranking_vida_paises(mapa, registros):
    ranking = []

    for pais in mapa:
        datos = consultar_vida_pais(registros, pais[0])

        registro = [pais[0], datos[3]]
        ranking.append(registro)

    ranking.sort(key=obtener_porcentaje_ranking, reverse=True)

    return ranking


# E: utiliza mapa y vida_territorios.
# S: ventana con el ranking de vida.
def mostrar_ranking_vida():
    ranking = ranking_vida_paises(mapa, vida_territorios)

    mensaje = ""
    posicion = 1

    for registro in ranking:
        mensaje += (
            str(posicion) + ". " + registro[0] +
            ": " + str(round(registro[1], 2)) + "% de vida\n"
        )

        posicion += 1

    if mensaje == "":
        mensaje = "No hay países para mostrar."

    messagebox.showinfo(
        "Ranking por porcentaje de vida",
        mensaje,
        parent=ventana
    )


# Muestra los países ordenados por su extensión original
# E: utiliza mapa y vida_territorios
# S: ventana con el ranking de países

def mostrar_ranking_extension():
    ranking = extension_original_paises

    mensaje = ""
    posicion = 1

    for registro in ranking:
        mensaje += (
            str(posicion) + ". " + registro[0] +
            ": " + formatear_numero(registro[1]) + " km²\n"
        )

        posicion += 1

    if mensaje == "":
        mensaje = "No hay países para mostrar."

    messagebox.showinfo(
        "Ranking por extensión original",
        mensaje,
        parent=ventana
    )

# Busca los disparos recibidos por un territorio usando su ID.
# E: historial de disparos e identificador del territorio.
# S: lista de disparos recibidos por ese territorio.
# R: cada disparo debe incluir el identificador en la posición 7.
def consultar_historial_territorio(historial, identificador):
    encontrados = []

    for disparo in historial:
        if disparo[7] == identificador:
            encontrados.append(disparo)

    return encontrados

# Muestra los disparos recibidos por un territorio.
# E: solicita los nombres del país, estado y territorio.
# S: ventana con el historial del territorio.
# R: mapa e historial disponibles.
def mostrar_historial_territorio():
    pais = simpledialog.askstring(
        "Historial", "Ingrese el país:", parent=ventana
    )
    if pais is None:
        return

    estado = simpledialog.askstring(
        "Historial", "Ingrese el estado:", parent=ventana
    )
    if estado is None:
        return

    territorio = simpledialog.askstring(
        "Historial", "Ingrese el territorio:", parent=ventana
    )
    if territorio is None:
        return

    coincidencias = []

    for dato in vida_territorios:
        if (dato[0] == pais and
                dato[1] == estado and
                dato[2] == territorio):
            coincidencias.append(dato)

    registro = elegir_registro_territorio(coincidencias)

    if registro is None:
        return

    disparos = consultar_historial_territorio(
        historial_disparos, registro[5]
    )

    area_inicial = registro[3]
    area_viva = registro[4]

    if area_inicial > 0:
        porcentaje_vida = area_viva / area_inicial * 100
    else:
        porcentaje_vida = 0

    mensaje = (
        pais + " / " + estado + " / " + territorio +
        "\nExtensión original: " + formatear_numero(area_inicial) + " km²" +
        "\nExtensión viva: " + formatear_numero(area_viva) + " km²" +
        "\nVida restante: " + str(round(porcentaje_vida, 2)) + "%" +
        "\n\n"
    )

    if disparos == []:
        mensaje += "No hay disparos registrados contra este territorio."

    for disparo in disparos:
        mensaje += (
            "Modo: " + disparo[0] +
            "\nClave: " + disparo[1] +
            "\nPaís de origen: " + disparo[2] +
            "\nTipo de misil: " + disparo[3] +
            "\nCantidad: " + str(disparo[4]) +
            "\nDestino: " + str(disparo[5]) +
            "\n\n"
        )

    ventana_historial = tk.Toplevel(ventana)
    ventana_historial.title("Historial del territorio")
    ventana_historial.geometry("600x450")

    texto = tk.Text(ventana_historial, wrap="word")
    barra = tk.Scrollbar(ventana_historial, command=texto.yview)
    texto.config(yscrollcommand=barra.set)

    barra.pack(side="right", fill="y")
    texto.pack(side="left", fill="both", expand=True)

    texto.insert("1.0", mensaje)
    texto.config(state="disabled")

# Busca los disparos que alcanzaron territorios de un país.
# E: historial de disparos y nombre del país afectado.
# S: lista de disparos recibidos por ese país.

def consultar_historial_pais(historial, nombre_pais):
    encontrados = []

    for disparo in historial:
        territorio = disparo[6]

        if territorio != []:
            if territorio[0] == nombre_pais:
                encontrados.append(disparo)

    return encontrados


# Esot muestra los disparos recibidos por un país
def mostrar_historial_pais():
    nombre = simpledialog.askstring(
        "Historial del país",
        "Ingrese el nombre del país:",
        parent=ventana
    )

    if nombre is None:
        return

    existe = False

    for pais in mapa:
        if pais[0] == nombre:
            existe = True
            break

    if not existe:
        messagebox.showerror(
            "País no encontrado",
            "El país indicado no existe en el mapa.",
            parent=ventana
        )
        return

    disparos = consultar_historial_pais(
        historial_disparos, nombre
    )

    extension_original = 0

    for pais in extension_original_paises:
        if pais[0] == nombre:
            extension_original = pais[1]
            break

    datos_vida = consultar_vida_pais(vida_territorios, nombre)
    porcentaje_vida = datos_vida[3]

    mensaje = (
        "País: " + nombre +
        "\nExtensión original: " + formatear_numero(extension_original) + " km²" +
        "\nVida restante: " + str(round(porcentaje_vida, 2)) + "%" +
        "\n\n"
    )

    if disparos == []:
        mensaje += "No hay disparos registrados contra este país."

    estados = []

    for disparo in disparos:
        nombre_estado = disparo[6][1]

        if nombre_estado not in estados:
            estados.append(nombre_estado)

    for nombre_estado in estados:
        mensaje += "\nEstado: " + nombre_estado + "\n"
        territorios = []

        for disparo in disparos:
            destino = disparo[6]
            identificador = disparo[7]

            if destino[1] == nombre_estado:
                dato = [identificador, destino[2]]

                if dato not in territorios:
                    territorios.append(dato)

        for dato in territorios:
            identificador = dato[0]
            nombre_territorio = dato[1]

            mensaje += (
                "\tTerritorio: " + nombre_territorio +
                " | ID: " + str(identificador) + "\n"
            )

            for disparo in disparos:
                destino = disparo[6]

                if (destino[1] == nombre_estado and
                        disparo[7] == identificador):
                    mensaje += (
                        "\t\tModo: " + disparo[0] +
                        "\n\t\tClave: " + disparo[1] +
                        "\n\t\tPaís de origen: " + disparo[2] +
                        "\n\t\tTipo de misil: " + disparo[3] +
                        "\n\t\tCantidad: " + str(disparo[4]) +
                        "\n\t\tDestino: " + str(disparo[5]) +
                        "\n\n"
                    )
                    

    ventana_historial = tk.Toplevel(ventana)
    ventana_historial.title("Historial del país")
    ventana_historial.geometry("600x450")

    texto = tk.Text(ventana_historial, wrap="word")
    barra = tk.Scrollbar(ventana_historial, command=texto.yview)
    texto.config(yscrollcommand=barra.set)

    barra.pack(side="right", fill="y")
    texto.pack(side="left", fill="both", expand=True)

    texto.insert("1.0", mensaje)
    texto.config(state="disabled")


# Construye el listado de países estados y territorios
# E: mapa y registros de vida de los territorios
# S: texto con la jerarquía, porcentajes y áreas
# R: registros con área inicial en posición 3 y viva en 4


def construir_listado_planeta(mapa, registros):
    mensaje = ""

    for pais in mapa:
        nombre_pais = pais[0]
        datos_pais = consultar_vida_pais(registros, nombre_pais)

        mensaje += (
            "País: " + nombre_pais +
            "\nVida: " + str(round(datos_pais[3], 2)) + "%" +
            " | Extensión: " + formatear_numero(datos_pais[0]) + " km²" +
            " | Muertos: " + formatear_numero(datos_pais[2]) + " km²\n"
        )

        for estado in pais[1]:
            nombre_estado = estado[0]
            datos_estado = consultar_vida_estado(
                registros, nombre_pais, nombre_estado
            )

            mensaje += (
                "\n\tEstado: " + nombre_estado +
                "\n\tVida: " + str(round(datos_estado[3], 2)) + "%" +
                " | Extensión: " + formatear_numero(datos_estado[0]) + " km²" +
                " | Muertos: " + formatear_numero(datos_estado[2]) + " km²\n"
            )

            for registro in registros:
                if (registro[0] == nombre_pais and
                        registro[1] == nombre_estado):
                    area_inicial = registro[3]
                    area_viva = registro[4]
                    area_muerta = area_inicial - area_viva

                    if area_inicial > 0:
                        porcentaje = area_viva / area_inicial * 100
                    else:
                        porcentaje = 0

                    mensaje += (
                        "\n\t\tTerritorio: " + registro[2] +
                        "\n\t\tVida: " + str(round(porcentaje, 2)) + "%" +
                        " | Extensión: " + formatear_numero(area_inicial) + " km²" +
                        " | Muertos: " + formatear_numero(area_muerta) + " km²\n"
                    )

        mensaje += "\n\n"

    return mensaje


# Muestra el listado del planeta
# E: utiliza el mapa y los registros de vida
# S: ventana con países, estados y territorios

def mostrar_listado_planeta():
    mensaje = construir_listado_planeta(mapa, vida_territorios)

    ventana_listado = tk.Toplevel(ventana)
    ventana_listado.title("Listado del planeta")
    ventana_listado.geometry("850x500")

    texto = tk.Text(ventana_listado, wrap="word")
    barra = tk.Scrollbar(ventana_listado, command=texto.yview)
    texto.config(yscrollcommand=barra.set)

    barra.pack(side="right", fill="y")
    texto.pack(side="left", fill="both", expand=True)

    texto.insert("1.0", mensaje)
    texto.config(state="disabled")
    
# Dibuja las escalas de coordenadas y una cuadrícula de referencia
# E: utiliza el canvas del mapa y los canvas de las dos escalas
# S: longitudes de -180 a 180 y latitudes de 90 a -90 estan cada 30 grados

def dibujar_escala_coordenadas():
    escala_longitud.delete("all")
    escala_latitud.delete("all")
    canvas.delete("cuadricula")

    escala_longitud.create_text(
        ANCHO_MAPA / 2, 12, text="Longitud (grados)", font=("Calibri", 10, "bold")
    )
    escala_latitud.create_text(
        12, ALTO_MAPA / 2, text="Latitud (grados)",
        angle=90, font=("Calibri", 10, "bold")
    )

    for longitud in range(-180, 181, 30):
        x = longitud_a_x(longitud)
        ancla = "center"
        if longitud == -180:
            ancla = "w"
        elif longitud == 180:
            ancla = "e"

        escala_longitud.create_text(
            x, 32, text=str(longitud) + "°", anchor=ancla, font=("Calibri", 9)
        )
        escala_longitud.create_line(x, 43, x, 49, fill="gray")
        canvas.create_line(
            x, 0, x, ALTO_MAPA, fill="#8caeb8",
            dash=(2, 4), tags="cuadricula"
        )

    for latitud in range(-90, 91, 30):
        y = latitud_a_y(latitud)
        ancla = "e"
        if latitud == 90:
            ancla = "ne"
        elif latitud == -90:
            ancla = "se"

        escala_latitud.create_text(
            65, y, text=str(latitud) + "°", anchor=ancla, font=("Calibri", 9)
        )
        escala_latitud.create_line(70, y, 77, y, fill="gray")
        canvas.create_line(
            0, y, ANCHO_MAPA, y, fill="#8caeb8",
            dash=(2, 4), tags="cuadricula"
        )

    canvas.create_line(
        0, latitud_a_y(0), ANCHO_MAPA, latitud_a_y(0),
        fill="#496b78", width=2, tags="cuadricula"
    )
    canvas.create_line(
        longitud_a_x(0), 0, longitud_a_x(0), ALTO_MAPA,
        fill="#496b78", width=2, tags="cuadricula"
    )
    canvas.tag_lower("cuadricula")


# Escribe el país en el centro de un territorio y actualiza su nombre.
# E: registro de vida con país, ID y territorio completo.
# S: texto centrado y ligado a la etiqueta del rectángulo.

def dibujar_nombre_pais(registro):
    identificador = str(registro[5])
    etiqueta_nombre = "nombre_pais_" + identificador
    canvas.delete(etiqueta_nombre)

    if registro[4] <= 0:
        return

    puntos = registro[6][1]
    posicion1 = punto_a_canvas(puntos[0])
    posicion2 = punto_a_canvas(puntos[1])
    centro_x = (posicion1[0] + posicion2[0]) / 2
    centro_y = (posicion1[1] + posicion2[1]) / 2
    ancho = abs(posicion2[0] - posicion1[0])
    alto = abs(posicion2[1] - posicion1[1])

    texto = canvas.create_text(
        centro_x, centro_y, text=registro[0], fill="#102a12",
        font=("Arial", 10, "bold"), justify="center",
        width=max(1, ancho - 6),
        tags=("territorio_" + identificador, etiqueta_nombre)
    )

    # Reduce la letra si el nombre no cabe en el rectángulo.
    for tamano in range(10, 4, -1):
        canvas.itemconfig(texto, font=("Arial", tamano, "bold"))
        limites = canvas.bbox(texto)
        if limites is not None:
            if (limites[2] - limites[0] <= ancho and
                    limites[3] - limites[1] <= alto):
                break


# ---------------------------------------
# GUI
# ---------------------------------------
historial_disparos = []

ventana = tk.Tk()
ventana.title("AI Revolution")
ventana.geometry("1000x650")
icono = tk.PhotoImage(master=ventana, file="icono.png")
ventana.iconphoto(True, icono)
parent = ventana

marco_mapa = tk.Frame(ventana)
marco_mapa.pack(pady=5)

escala_longitud = tk.Canvas(
    marco_mapa, width=ANCHO_MAPA, height=50,
    highlightthickness=0
)
escala_longitud.grid(row=0, column=1)

escala_latitud = tk.Canvas(
    marco_mapa, width=78, height=ALTO_MAPA,
    highlightthickness=0
)
escala_latitud.grid(row=1, column=0)

canvas = tk.Canvas(
    marco_mapa, width=ANCHO_MAPA, height=ALTO_MAPA,
    bg="lightblue", highlightthickness=0
)
canvas.grid(row=1, column=1)
dibujar_escala_coordenadas()

#Aquí se verifica si se encontró un error en el mapa
mapa_valido = False
mapa = leer_archivo("mapa.txt")
if mapa is not None:
    error = revisar_coordenadas_mapa(mapa)

    if error == "":
        error = revisar_traslapes(mapa)

    if error != "":
        messagebox.showerror("Error en el mapa", error, parent=ventana)
    else:
        mapa_original = copy.deepcopy(mapa)
        mapa_muertos = []
        vida_territorios = crear_vida_territorios(mapa)
        extension_original_paises = ranking_extension_paises(
            mapa, vida_territorios
        )
        mapa_valido = True

        for pais in mapa:
            estados = pais[1]

            for estado in estados:
                territorios = estado[1]

                for territorio in territorios:
                    puntos = territorio[1]

                    punto1 = puntos[0]
                    punto2 = puntos[1]

                    posicion1 = punto_a_canvas(punto1)
                    posicion2 = punto_a_canvas(punto2)
                    registro = buscar_vida_por_territorio(
                        vida_territorios,
                        territorio
                    )

                    etiqueta = "territorio_" + str(registro[5])

                    canvas.create_rectangle(
                        posicion1[0], posicion1[1],
                        posicion2[0], posicion2[1],
                        fill="#0ddb1e",
                        outline="#3e6e12",
                        tags=etiqueta,
                       

                    )
                    dibujar_nombre_pais(registro)

misiles = leer_archivo("misiles.txt")

if mapa_valido and misiles is not None:
    marco_botones = tk.Frame(ventana)
    marco_botones.pack(pady=10)

    boton_manual = tk.Button(
        marco_botones,
        text="IA manual",
        width=20,
        height=2,
        command=seleccionar_clave_manual
    )
    boton_manual.pack(side="left", padx=5)

    boton_aleatorio = tk.Button(
        marco_botones,
        text="IA aleatoria",
        width=20,
        height=2,
        command=seleccionar_clave_aleatoria
    )
    boton_aleatorio.pack(side="left", padx=5)

    boton_consulta_paises = tk.Button(
        marco_botones,
        width=20,
        height=2,
        text="Vida de países",
        command=mostrar_vida_paises
    )
    boton_consulta_paises.pack(side="left", padx=5)

    boton_consulta_estados = tk.Button(
        marco_botones,
        width=20,
        height=2,
        text="Vida de estados",
        command=mostrar_vida_estados
    )
    boton_consulta_estados.pack(side="left", padx=5)

    boton_consulta_territorios = tk.Button(
        marco_botones,
        width=20,
        height=2,
        text="Vida de territorios",
        command=mostrar_listado_planeta
    )
    boton_consulta_territorios.pack(side="left", padx=5)
    
    boton_listado_planeta = tk.Button(
        ventana,
        text="Listado del planeta",
        command=mostrar_listado_planeta
    )
    boton_listado_planeta.pack(pady=5)


    marco_rankings = tk.Frame(ventana)
    marco_rankings.pack(pady=5)

    boton_ranking_extension = tk.Button(
        marco_rankings,
        text="Ranking por extensión",
        command=mostrar_ranking_extension
    )
    boton_ranking_extension.pack(side="left", padx=5)

    boton_ranking_vida = tk.Button(
        marco_rankings,
        text="Ranking de vida",
        command=mostrar_ranking_vida
    )
    boton_ranking_vida.pack(side="left", padx=5)

    boton_historial_territorio = tk.Button(
        marco_rankings,
        text="Historial de territorio",
        command=mostrar_historial_territorio
    )
    boton_historial_territorio.pack(side="left", padx=5)

    boton_historial_pais = tk.Button(
        marco_rankings,
        text="Historial de país",
        command=mostrar_historial_pais
    )
    boton_historial_pais.pack(side="left", padx=5)

    boton_traslado = tk.Button(
        marco_rankings,
        text="Trasladar territorio",
        command=solicitar_traslado
    )
    boton_traslado.pack(side="left", padx=5)

    boton_ganador = tk.Button(
        marco_rankings,
        text="Ganador",
        command=mostrar_ganador
    )
    boton_ganador.pack(side="left", padx=5)
    boton_salir = tk.Button(
        ventana,
        text="Salir",
        command=ventana.destroy
    )
    boton_salir.pack(pady=5)


# Cargar la imagen de la brújula
imagen_brujula = tk.PhotoImage(
    master=ventana,
    file="brujula.png"
)

# Mostrarla en la esquina superior derecha del mapa
canvas.create_image(
    ANCHO_MAPA - 10,
    10,
    image=imagen_brujula,
    anchor="ne",
    tags="brujula"
)
#------------------------------------
# AREA DE PRUEBAS


#-------------------------------------------

# ---------------------------------------
# Iniciar GUI
# ---------------------------------------

ventana.mainloop()

