"""
Sistema de Gestion de Pedidos - FloraExport
Empresa Exportadora de Ramilletes de Flores

Estructuras de datos:
  - Lista enlazada : inventario de flores
  - Pila (LIFO)   : historial de operaciones con deshacer
  - Cola (FIFO)   : pedidos en logistica y envios
"""

from datetime import datetime


# =============================================================================
#  ESTRUCTURAS DE DATOS BASE
# =============================================================================

class NodoLista:
    """Nodo de la lista enlazada para el inventario."""

    def __init__(self, flor):
        self.flor      = flor
        self.siguiente = None


class ListaEnlazada:
    """Lista enlazada que almacena el inventario de flores."""

    def __init__(self):
        self.cabeza  = None
        self._tamano = 0

    def agregar(self, flor):
        """Inserta una flor al final de la lista."""
        nuevo = NodoLista(flor)
        if self.cabeza is None:
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo
        self._tamano += 1

    def eliminar(self, codigo):
        """Elimina la flor con el codigo dado. Retorna el objeto o None."""
        actual   = self.cabeza
        anterior = None
        while actual:
            if actual.flor.codigo == codigo:
                if anterior:
                    anterior.siguiente = actual.siguiente
                else:
                    self.cabeza = actual.siguiente
                self._tamano -= 1
                return actual.flor
            anterior = actual
            actual   = actual.siguiente
        return None

    def buscar(self, codigo):
        """Retorna la flor con el codigo dado o None."""
        actual = self.cabeza
        while actual:
            if actual.flor.codigo == codigo:
                return actual.flor
            actual = actual.siguiente
        return None

    def buscar_por_nombre(self, nombre, color=None):
        """Retorna lista de flores que coincidan con nombre y/o color."""
        resultados = []
        actual     = self.cabeza
        while actual:
            coincide_nombre = nombre.lower() in actual.flor.nombre.lower()
            coincide_color  = (color is None) or (color.lower() in actual.flor.color.lower())
            if coincide_nombre and coincide_color:
                resultados.append(actual.flor)
            actual = actual.siguiente
        return resultados

    def listar(self):
        """Retorna todos los elementos como lista de Python."""
        resultado = []
        actual    = self.cabeza
        while actual:
            resultado.append(actual.flor)
            actual = actual.siguiente
        return resultado

    def tamano(self):
        """Retorna el numero de flores en el inventario."""
        return self._tamano


class NodoPila:
    """Nodo de la pila para el historial."""

    def __init__(self, valor):
        self.valor     = valor
        self.siguiente = None


class Pila:
    """Pila LIFO para historial de operaciones con soporte de deshacer."""

    def __init__(self):
        self.cima   = None
        self.tamano = 0

    def push(self, valor):
        """Apila una accion en el historial."""
        nuevo           = NodoPila(valor)
        nuevo.siguiente = self.cima
        self.cima       = nuevo
        self.tamano    += 1

    def pop(self):
        """Desapila y retorna la ultima accion."""
        if self.esta_vacia():
            raise IndexError("historial vacio")
        valor       = self.cima.valor
        self.cima   = self.cima.siguiente
        self.tamano -= 1
        return valor

    def peek(self):
        """Retorna la ultima accion sin eliminarla."""
        if self.esta_vacia():
            raise IndexError("historial vacio")
        return self.cima.valor

    def esta_vacia(self):
        """Retorna True si el historial esta vacio."""
        return self.cima is None

    def listar(self):
        """Retorna todas las acciones desde la mas reciente."""
        resultado = []
        actual    = self.cima
        while actual:
            resultado.append(actual.valor)
            actual = actual.siguiente
        return resultado


class NodoCola:
    """Nodo de la cola FIFO para envios."""

    def __init__(self, dato):
        self.dato      = dato
        self.siguiente = None


class Cola:
    """Cola FIFO para gestion de pedidos en logistica."""

    def __init__(self):
        self.frente = None
        self.final  = None
        self.tamano = 0

    def enqueue(self, dato):
        """Agrega un pedido al final de la cola."""
        nuevo = NodoCola(dato)
        if self.final is None:
            self.frente = nuevo
            self.final  = nuevo
        else:
            self.final.siguiente = nuevo
            self.final           = nuevo
        self.tamano += 1

    def dequeue(self):
        """Elimina y retorna el pedido al frente de la cola."""
        if self.esta_vacia():
            raise IndexError("cola de envios vacia")
        dato        = self.frente.dato
        self.frente = self.frente.siguiente
        if self.frente is None:
            self.final = None
        self.tamano -= 1
        return dato

    def esta_vacia(self):
        """Retorna True si no hay pedidos en la cola."""
        return self.frente is None

    def listar(self):
        """Retorna todos los pedidos desde el frente."""
        resultado = []
        actual    = self.frente
        while actual:
            resultado.append(actual.dato)
            actual = actual.siguiente
        return resultado


# =============================================================================
#  MODELOS DE DOMINIO
# =============================================================================

# Estados validos de un pedido
ESTADOS_PEDIDO = ["Pendiente", "En preparacion", "Enviado", "Entregado"]

# Umbral de stock bajo
UMBRAL_STOCK_BAJO = 30

# Tamanos de ramillete disponibles
TAMANOS = ["Pequeno (5-8 flores)", "Mediano (10-15 flores)", "Grande (20-25 flores)"]


class Flor:
    """Representa una variedad de flor en el inventario."""

    def __init__(self, codigo, nombre, color, stock, precio):
        self.codigo = codigo.upper()
        self.nombre = nombre
        self.color  = color
        self.stock  = stock
        self.precio = precio

    def stock_bajo(self):
        """Indica si el stock esta por debajo del umbral critico."""
        return self.stock < UMBRAL_STOCK_BAJO

    def __str__(self):
        alerta = " [STOCK BAJO]" if self.stock_bajo() else ""
        return (f"{self.codigo} | {self.nombre:<12} | {self.color:<10} | "
                f"Stock: {self.stock:>4} | ${self.precio:.2f}{alerta}")


class ItemPedido:
    """Representa una linea dentro de un pedido (flor + cantidad)."""

    def __init__(self, flor, cantidad):
        self.codigo_flor = flor.codigo
        self.nombre_flor = flor.nombre
        self.color_flor  = flor.color
        self.cantidad    = cantidad
        self.precio_unit = flor.precio

    def subtotal(self):
        """Retorna el subtotal de esta linea."""
        return self.cantidad * self.precio_unit

    def __str__(self):
        return (f"  {self.nombre_flor} ({self.color_flor}) "
                f"x{self.cantidad} @ ${self.precio_unit:.2f} "
                f"= ${self.subtotal():.2f}")


class Pedido:
    """Representa un pedido completo de un cliente."""

    _contador = 0

    def __init__(self, nombre_cliente, telefono, pais_destino, tamano):
        Pedido._contador += 1
        self.id_pedido      = f"P{Pedido._contador:03d}"
        self.nombre_cliente = nombre_cliente
        self.telefono       = telefono
        self.pais_destino   = pais_destino
        self.tamano         = tamano
        self.items          = []
        self.estado         = "Pendiente"
        self.timestamp      = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.notas          = ""

    def agregar_item(self, item):
        """Agrega una linea de flor al pedido."""
        self.items.append(item)

    def total(self):
        """Retorna el total del pedido."""
        return sum(i.subtotal() for i in self.items)

    def resumen(self):
        """Retorna un resumen legible del pedido."""
        lineas = [
            f"\n  {'='*50}",
            f"  Pedido ID  : {self.id_pedido}",
            f"  Cliente    : {self.nombre_cliente}",
            f"  Telefono   : {self.telefono}",
            f"  Destino    : {self.pais_destino}",
            f"  Tamano     : {self.tamano}",
            f"  Estado     : {self.estado}",
            f"  Fecha      : {self.timestamp}",
            f"  {'─'*50}",
            f"  Flores:",
        ]
        for item in self.items:
            lineas.append(str(item))
        lineas.append(f"  {'─'*50}")
        lineas.append(f"  TOTAL      : ${self.total():.2f}")
        if self.notas:
            lineas.append(f"  Notas      : {self.notas}")
        lineas.append(f"  {'='*50}")
        return "\n".join(lineas)

    def __str__(self):
        flores_resumen = ", ".join(
            f"{i.nombre_flor} x{i.cantidad}" for i in self.items
        ) or "sin flores"
        return (f"[{self.id_pedido}] {self.nombre_cliente:<18} | "
                f"{self.pais_destino:<15} | {self.estado:<15} | "
                f"${self.total():.2f} | {flores_resumen}")


# =============================================================================
#  SISTEMA PRINCIPAL
# =============================================================================

class SistemaFloraExport:
    """
    Sistema central que integra las tres estructuras de datos:
      - ListaEnlazada : inventario de flores
      - Pila          : historial con deshacer
      - Cola          : cola de envios FIFO
    """

    def __init__(self):
        self.inventario  = ListaEnlazada()
        self.historial   = Pila()
        self.cola_envios = Cola()
        self.pedidos     = []          # lista Python para busqueda rapida por ID
        self._cargar_inventario_inicial()

    # ── Inventario inicial ────────────────────────────────────────────────────

    def _cargar_inventario_inicial(self):
        """Carga el catalogo base de flores de FloraExport."""
        flores_iniciales = [
            Flor("F001", "Rosa",      "Rojo",     182, 1.50),
            Flor("F002", "Rosa",      "Blanco",   142, 1.50),
            Flor("F003", "Rosa",      "Rosa",     120, 1.50),
            Flor("F004", "Tulipan",   "Amarillo",  68, 2.00),
            Flor("F005", "Tulipan",   "Rojo",      75, 2.00),
            Flor("F006", "Girasol",   "Amarillo",  50, 2.50),
            Flor("F007", "Orquidea",  "Blanco",    18, 5.00),
            Flor("F008", "Orquidea",  "Morado",    25, 5.50),
            Flor("F009", "Clavel",    "Rojo",     100, 1.00),
            Flor("F010", "Lirio",     "Blanco",    60, 3.00),
        ]
        for flor in flores_iniciales:
            self.inventario.agregar(flor)

    # ── Inventario ────────────────────────────────────────────────────────────

    def mostrar_inventario(self):
        """Muestra el inventario completo con alertas de stock bajo."""
        flores = self.inventario.listar()
        if not flores:
            print("  Inventario vacio.")
            return
        print(f"\n  {'─'*70}")
        print(f"  {'ID':<6} {'Nombre':<14} {'Color':<12} {'Stock':>6} {'Precio':>8}")
        print(f"  {'─'*70}")
        total_flores   = 0
        flores_en_riesgo = 0
        for f in flores:
            alerta = "  [STOCK BAJO]" if f.stock_bajo() else ""
            print(f"  {f.codigo:<6} {f.nombre:<14} {f.color:<12} "
                  f"{f.stock:>6} | ${f.precio:>6.2f}{alerta}")
            total_flores   += f.stock
            if f.stock_bajo():
                flores_en_riesgo += 1
        print(f"  {'─'*70}")
        print(f"  Total de flores en inventario: {total_flores}")
        print(f"  Flores con stock bajo: {flores_en_riesgo}")

    def registrar_lote(self, codigo, cantidad):
        """Agrega stock a una flor existente o permite agregar una nueva."""
        flor = self.inventario.buscar(codigo.upper())
        if flor is None:
            print(f"  Flor '{codigo.upper()}' no encontrada.")
            return False
        stock_anterior = flor.stock
        flor.stock    += cantidad
        self.historial.push({
            "accion"        : "LOTE",
            "codigo"        : flor.codigo,
            "nombre"        : flor.nombre,
            "color"         : flor.color,
            "stock_anterior": stock_anterior,
            "cantidad"      : cantidad,
            "timestamp"     : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })
        print(f"\n  Actualizacion de inventario:")
        print(f"  {flor.nombre} ({flor.color}): "
              f"Stock anterior: {stock_anterior} -> Nuevo stock: {flor.stock}")
        print(f"\n  Entrada registrada en el historial:")
        print(f"  Fecha     : {self.historial.peek()['timestamp']}")
        print(f"  Tipo      : Entrada de lote")
        print(f"  Flor      : {flor.nombre} {flor.color}")
        print(f"  Cantidad  : +{cantidad}")
        print(f"  Nuevo stock: {flor.stock}")
        return True

    def agregar_nueva_flor(self, codigo, nombre, color, stock, precio):
        """Agrega una variedad de flor nueva al inventario."""
        if self.inventario.buscar(codigo.upper()):
            print(f"  Ya existe una flor con codigo '{codigo.upper()}'.")
            return False
        nueva = Flor(codigo, nombre, color, stock, precio)
        self.inventario.agregar(nueva)
        self.historial.push({
            "accion"   : "NUEVA_FLOR",
            "flor"     : Flor(codigo, nombre, color, stock, precio),
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })
        print(f"  Flor '{nombre} ({color})' agregada con codigo {codigo.upper()}.")
        return True

    def actualizar_stock_manual(self, codigo, nuevo_stock):
        """Actualiza el stock de una flor manualmente."""
        flor = self.inventario.buscar(codigo.upper())
        if flor is None:
            print(f"  Flor '{codigo.upper()}' no encontrada.")
            return False
        stock_anterior = flor.stock
        flor.stock     = nuevo_stock
        self.historial.push({
            "accion"        : "ACTUALIZAR_STOCK",
            "codigo"        : flor.codigo,
            "nombre"        : flor.nombre,
            "color"         : flor.color,
            "stock_anterior": stock_anterior,
            "stock_nuevo"   : nuevo_stock,
            "timestamp"     : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })
        print(f"  Stock actualizado: {flor.nombre} ({flor.color}) "
              f"{stock_anterior} -> {nuevo_stock}")
        return True

    def ver_alertas_stock(self):
        """Muestra solo las flores con stock bajo el umbral."""
        flores = [f for f in self.inventario.listar() if f.stock_bajo()]
        if not flores:
            print(f"  Sin alertas. Todas las flores tienen stock >= {UMBRAL_STOCK_BAJO}.")
            return
        print(f"\n  Flores con stock bajo (< {UMBRAL_STOCK_BAJO} unidades):")
        for f in flores:
            print(f"  {f}")

    def buscar_flor(self, nombre=None, color=None):
        """Busca flores por nombre y/o color."""
        if nombre is None and color is None:
            return self.inventario.listar()
        resultados = self.inventario.buscar_por_nombre(nombre or "", color)
        return resultados

    # ── Pedidos ───────────────────────────────────────────────────────────────

    def crear_pedido(self, nombre_cliente, telefono, pais_destino, tamano, items_solicitados):
        """
        Crea un pedido verificando disponibilidad en inventario.
        items_solicitados: lista de tuplas (codigo_flor, cantidad)
        """
        # Validar disponibilidad antes de comprometer stock
        validados = []
        for codigo, cantidad in items_solicitados:
            flor = self.inventario.buscar(codigo.upper())
            if flor is None:
                print(f"  Error: Flor '{codigo.upper()}' no existe en inventario.")
                return None
            if flor.stock < cantidad:
                print(f"  Error: Stock insuficiente para {flor.nombre} ({flor.color}). "
                      f"Disponible: {flor.stock}, solicitado: {cantidad}.")
                return None
            validados.append((flor, cantidad))

        # Crear pedido y descontar stock
        pedido = Pedido(nombre_cliente, telefono, pais_destino, tamano)
        for flor, cantidad in validados:
            item = ItemPedido(flor, cantidad)
            pedido.agregar_item(item)
            flor.stock -= cantidad

        self.pedidos.append(pedido)
        self.historial.push({
            "accion"   : "CREAR_PEDIDO",
            "id_pedido": pedido.id_pedido,
            "items"    : [(f.codigo, c) for f, c in validados],
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })
        return pedido

    def buscar_pedido(self, id_pedido):
        """Retorna el pedido con el ID dado o None."""
        for p in self.pedidos:
            if p.id_pedido == id_pedido.upper():
                return p
        return None

    def cambiar_estado_pedido(self, id_pedido, nuevo_estado):
        """Cambia el estado de un pedido y lo encola en envios si corresponde."""
        if nuevo_estado not in ESTADOS_PEDIDO:
            print(f"  Estado invalido. Opciones: {', '.join(ESTADOS_PEDIDO)}")
            return False
        pedido = self.buscar_pedido(id_pedido)
        if pedido is None:
            print(f"  Pedido '{id_pedido}' no encontrado.")
            return False
        estado_anterior = pedido.estado
        pedido.estado   = nuevo_estado

        self.historial.push({
            "accion"         : "CAMBIO_ESTADO",
            "id_pedido"      : pedido.id_pedido,
            "estado_anterior": estado_anterior,
            "estado_nuevo"   : nuevo_estado,
            "timestamp"      : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })

        # Encolar automaticamente al pasar a "Enviado"
        if nuevo_estado == "Enviado":
            self.cola_envios.enqueue(pedido)
            print(f"  Pedido {pedido.id_pedido} encolado en logistica de envios.")

        print(f"  Estado actualizado: {estado_anterior} -> {nuevo_estado}")
        return True

    def modificar_notas_pedido(self, id_pedido, notas):
        """Agrega o modifica las notas de un pedido."""
        pedido = self.buscar_pedido(id_pedido)
        if pedido is None:
            print(f"  Pedido '{id_pedido}' no encontrado.")
            return False
        notas_anteriores = pedido.notas
        pedido.notas     = notas
        self.historial.push({
            "accion"          : "MODIFICAR_NOTAS",
            "id_pedido"       : pedido.id_pedido,
            "notas_anteriores": notas_anteriores,
            "notas_nuevas"    : notas,
            "timestamp"       : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })
        print(f"  Notas del pedido {id_pedido} actualizadas.")
        return True

    def eliminar_pedido(self, id_pedido):
        """Elimina un pedido y restaura el stock de sus flores."""
        pedido = self.buscar_pedido(id_pedido)
        if pedido is None:
            print(f"  Pedido '{id_pedido}' no encontrado.")
            return False
        if pedido.estado in ("Enviado", "Entregado"):
            print(f"  No se puede eliminar un pedido en estado '{pedido.estado}'.")
            return False
        # Restaurar stock
        for item in pedido.items:
            flor = self.inventario.buscar(item.codigo_flor)
            if flor:
                flor.stock += item.cantidad
        self.pedidos.remove(pedido)
        self.historial.push({
            "accion"   : "ELIMINAR_PEDIDO",
            "pedido"   : pedido,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })
        print(f"  Pedido {id_pedido} eliminado. Stock restaurado.")
        return True

    def listar_pedidos(self, filtro_estado=None):
        """Muestra todos los pedidos, opcionalmente filtrados por estado."""
        pedidos = self.pedidos
        if filtro_estado:
            pedidos = [p for p in pedidos if p.estado == filtro_estado]
        if not pedidos:
            print("  No hay pedidos registrados.")
            return
        print(f"\n  {'─'*85}")
        print(f"  {'ID':<7} {'Cliente':<20} {'Destino':<16} {'Estado':<16} "
              f"{'Total':>8} {'Flores'}")
        print(f"  {'─'*85}")
        for p in pedidos:
            flores_str = ", ".join(
                f"{i.nombre_flor} x{i.cantidad}" for i in p.items
            )[:35]
            print(f"  {p.id_pedido:<7} {p.nombre_cliente:<20} {p.pais_destino:<16} "
                  f"{p.estado:<16} ${p.total():>7.2f}  {flores_str}")
        print(f"  {'─'*85}")
        print(f"  Total: {len(pedidos)} pedido(s)")

    # ── Logistica ─────────────────────────────────────────────────────────────

    def procesar_siguiente_envio(self):
        """Despacha el primer pedido de la cola de envios."""
        if self.cola_envios.esta_vacia():
            print("  No hay pedidos en la cola de envios.")
            return None
        pedido        = self.cola_envios.dequeue()
        pedido.estado = "Entregado"
        self.historial.push({
            "accion"   : "ENTREGAR_PEDIDO",
            "id_pedido": pedido.id_pedido,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })
        print(f"\n  Pedido despachado:")
        print(f"  ID       : {pedido.id_pedido}")
        print(f"  Cliente  : {pedido.nombre_cliente}")
        print(f"  Destino  : {pedido.pais_destino}")
        print(f"  Total    : ${pedido.total():.2f}")
        print(f"  Estado   : Entregado")
        print(f"  Pedidos restantes en cola: {self.cola_envios.tamano}")
        return pedido

    def mostrar_cola_envios(self):
        """Muestra los pedidos en la cola de envios en orden de despacho."""
        pedidos = self.cola_envios.listar()
        if not pedidos:
            print("  La cola de envios esta vacia.")
            return
        print(f"\n  Cola de envios ({len(pedidos)} pedido(s), orden FIFO):")
        print(f"  {'─'*60}")
        for i, p in enumerate(pedidos, 1):
            print(f"  {i}. {p.id_pedido} | {p.nombre_cliente:<18} | {p.pais_destino}")
        print(f"  {'─'*60}")
        print(f"  Proximo en despachar: {pedidos[0].id_pedido} - {pedidos[0].nombre_cliente}")

    # ── Historial / Deshacer ──────────────────────────────────────────────────

    def mostrar_historial(self, limite=10):
        """Muestra las ultimas acciones del historial."""
        acciones = self.historial.listar()
        if not acciones:
            print("  Historial vacio.")
            return
        print(f"\n  Historial de operaciones (ultimas {min(limite, len(acciones))}):")
        print(f"  {'─'*60}")
        for i, a in enumerate(acciones[:limite], 1):
            tipo = a["accion"]
            ts   = a.get("timestamp", "")
            if tipo == "CREAR_PEDIDO":
                detalle = f"Crear pedido {a['id_pedido']}"
            elif tipo == "CAMBIO_ESTADO":
                detalle = (f"Cambio estado {a['id_pedido']}: "
                           f"{a['estado_anterior']} -> {a['estado_nuevo']}")
            elif tipo == "LOTE":
                detalle = (f"Lote {a['nombre']} ({a['color']}): "
                           f"+{a['cantidad']} unidades")
            elif tipo == "ACTUALIZAR_STOCK":
                detalle = (f"Stock {a['nombre']} ({a['color']}): "
                           f"{a['stock_anterior']} -> {a['stock_nuevo']}")
            elif tipo == "NUEVA_FLOR":
                detalle = f"Nueva flor: {a['flor'].nombre} ({a['flor'].color})"
            elif tipo == "ELIMINAR_PEDIDO":
                detalle = f"Eliminar pedido {a['pedido'].id_pedido}"
            elif tipo == "MODIFICAR_NOTAS":
                detalle = f"Notas pedido {a['id_pedido']}"
            elif tipo == "ENTREGAR_PEDIDO":
                detalle = f"Entregar pedido {a['id_pedido']}"
            else:
                detalle = tipo
            print(f"  {i:>2}. [{ts}] {detalle}")
        print(f"  {'─'*60}")
        print(f"  Total en historial: {self.historial.tamano}")

    def deshacer(self):
        """Deshace la ultima operacion registrada en el historial."""
        if self.historial.esta_vacia():
            print("  No hay acciones para deshacer.")
            return False

        accion = self.historial.pop()
        tipo   = accion["accion"]

        if tipo == "CREAR_PEDIDO":
            pedido = self.buscar_pedido(accion["id_pedido"])
            if pedido:
                for item in pedido.items:
                    flor = self.inventario.buscar(item.codigo_flor)
                    if flor:
                        flor.stock += item.cantidad
                self.pedidos.remove(pedido)
            print(f"  Deshecho: creacion del pedido {accion['id_pedido']}. "
                  "Stock restaurado.")

        elif tipo == "CAMBIO_ESTADO":
            pedido = self.buscar_pedido(accion["id_pedido"])
            if pedido:
                pedido.estado = accion["estado_anterior"]
            print(f"  Deshecho: estado del pedido {accion['id_pedido']} "
                  f"restaurado a '{accion['estado_anterior']}'.")

        elif tipo == "LOTE":
            flor = self.inventario.buscar(accion["codigo"])
            if flor:
                flor.stock = accion["stock_anterior"]
            print(f"  Deshecho: lote de {accion['nombre']} ({accion['color']}). "
                  f"Stock restaurado a {accion['stock_anterior']}.")

        elif tipo == "ACTUALIZAR_STOCK":
            flor = self.inventario.buscar(accion["codigo"])
            if flor:
                flor.stock = accion["stock_anterior"]
            print(f"  Deshecho: actualizacion de stock de {accion['nombre']}. "
                  f"Restaurado a {accion['stock_anterior']}.")

        elif tipo == "NUEVA_FLOR":
            self.inventario.eliminar(accion["flor"].codigo)
            print(f"  Deshecho: nueva flor '{accion['flor'].nombre}' eliminada.")

        elif tipo == "ELIMINAR_PEDIDO":
            pedido = accion["pedido"]
            self.pedidos.append(pedido)
            for item in pedido.items:
                flor = self.inventario.buscar(item.codigo_flor)
                if flor:
                    flor.stock -= item.cantidad
            print(f"  Deshecho: pedido {pedido.id_pedido} restaurado.")

        elif tipo == "MODIFICAR_NOTAS":
            pedido = self.buscar_pedido(accion["id_pedido"])
            if pedido:
                pedido.notas = accion["notas_anteriores"]
            print(f"  Deshecho: notas del pedido {accion['id_pedido']} restauradas.")

        elif tipo == "ENTREGAR_PEDIDO":
            pedido = self.buscar_pedido(accion["id_pedido"])
            if pedido:
                pedido.estado = "Enviado"
                self.cola_envios.enqueue(pedido)
            print(f"  Deshecho: entrega del pedido {accion['id_pedido']} revertida.")

        return True


# =============================================================================
#  HELPERS DE ENTRADA
# =============================================================================

def pedir_entero(mensaje, minimo=0, maximo=None):
    """Solicita un entero validado dentro de un rango."""
    while True:
        try:
            valor = int(input(mensaje).strip())
            if valor < minimo:
                print(f"  El valor debe ser >= {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  El valor debe ser <= {maximo}.")
                continue
            return valor
        except ValueError:
            print("  Ingrese un numero entero valido.")


def pedir_float(mensaje, minimo=0.0):
    """Solicita un flotante validado."""
    while True:
        try:
            valor = float(input(mensaje).strip())
            if valor < minimo:
                print(f"  El valor debe ser >= {minimo}.")
                continue
            return valor
        except ValueError:
            print("  Ingrese un numero valido.")


def pedir_telefono(mensaje):
    """Solicita un numero de telefono de 7-15 digitos."""
    while True:
        tel = input(mensaje).strip()
        digitos = tel.replace("+", "").replace("-", "").replace(" ", "")
        if digitos.isdigit() and 7 <= len(digitos) <= 15:
            return tel
        print("  Telefono invalido. Debe contener entre 7 y 15 digitos.")


def pedir_no_vacio(mensaje):
    """Solicita un texto no vacio."""
    while True:
        val = input(mensaje).strip()
        if val:
            return val
        print("  Este campo no puede estar vacio.")


def seleccionar_opcion(opciones, mensaje="  Seleccione una opcion: "):
    """Muestra una lista numerada y retorna el indice seleccionado (0-based)."""
    for i, op in enumerate(opciones, 1):
        print(f"  {i}. {op}")
    while True:
        try:
            sel = int(input(mensaje).strip())
            if 1 <= sel <= len(opciones):
                return sel - 1
            print(f"  Ingrese un numero entre 1 y {len(opciones)}.")
        except ValueError:
            print("  Ingrese un numero valido.")


def pausar():
    """Pausa la ejecucion hasta que el usuario presione Enter."""
    input("\n  Presione Enter para continuar...")


# =============================================================================
#  MENUS
# =============================================================================

SEP = "=" * 58

def header(titulo):
    print(f"\n  {SEP}")
    print(f"  {titulo.center(56)}")
    print(f"  {SEP}")


# ── Modulo Inventario ─────────────────────────────────────────────────────────

def menu_inventario(sistema):
    while True:
        header("MODULO DE INVENTARIO DE FLORES")
        print("  Seleccione una operacion:")
        print("  1. Ver inventario completo")
        print("  2. Buscar flor por nombre/color")
        print("  3. Registrar nuevo lote de flores")
        print("  4. Agregar nueva variedad de flor")
        print("  5. Actualizar stock manualmente")
        print("  6. Ver alertas de stock")
        print("  7. Volver al menu principal")
        op = input("\n  Seleccione una opcion: ").strip()

        if op == "1":
            header("INVENTARIO COMPLETO DE FLORES")
            print("  Estructura actual: Lista enlazada de inventario\n")
            sistema.mostrar_inventario()
            pausar()

        elif op == "2":
            header("BUSCAR FLOR")
            nombre = input("  Nombre (dejar vacio para omitir): ").strip() or None
            color  = input("  Color  (dejar vacio para omitir): ").strip() or None
            if nombre is None and color is None:
                print("  Ingrese al menos un criterio de busqueda.")
            else:
                resultados = sistema.buscar_flor(nombre, color)
                if not resultados:
                    print("  No se encontraron flores con esos criterios.")
                else:
                    print(f"\n  Resultados ({len(resultados)}):")
                    for f in resultados:
                        print(f"  {f}")
            pausar()

        elif op == "3":
            header("REGISTRAR NUEVO LOTE")
            sistema.mostrar_inventario()
            print()
            codigo   = pedir_no_vacio("  Codigo de la flor (ej. F007): ").upper()
            cantidad = pedir_entero("  Cantidad de flores en el lote: ", minimo=1)
            precio   = input(f"  Precio por unidad (dejar vacio para mantener actual): ").strip()
            if precio:
                try:
                    flor = sistema.inventario.buscar(codigo)
                    if flor:
                        flor.precio = float(precio)
                except ValueError:
                    print("  Precio invalido, se mantiene el actual.")
            sistema.registrar_lote(codigo, cantidad)
            pausar()

        elif op == "4":
            header("AGREGAR NUEVA VARIEDAD")
            # Generar codigo sugerido
            flores      = sistema.inventario.listar()
            ultimo_num  = len(flores)
            cod_sugerido = f"F{ultimo_num + 1:03d}"
            print(f"  Codigo sugerido: {cod_sugerido}")
            codigo  = input(f"  Codigo (Enter para usar {cod_sugerido}): ").strip() or cod_sugerido
            nombre  = pedir_no_vacio("  Nombre de la flor  : ")
            color   = pedir_no_vacio("  Color              : ")
            stock   = pedir_entero("  Stock inicial      : ", minimo=0)
            precio  = pedir_float("  Precio por unidad  : ", minimo=0.01)
            sistema.agregar_nueva_flor(codigo, nombre, color, stock, precio)
            pausar()

        elif op == "5":
            header("ACTUALIZAR STOCK MANUAL")
            codigo     = pedir_no_vacio("  Codigo de la flor: ").upper()
            flor       = sistema.inventario.buscar(codigo)
            if flor:
                print(f"  Stock actual: {flor.stock}")
                nuevo_stock = pedir_entero("  Nuevo stock: ", minimo=0)
                sistema.actualizar_stock_manual(codigo, nuevo_stock)
            else:
                print(f"  Flor '{codigo}' no encontrada.")
            pausar()

        elif op == "6":
            header("ALERTAS DE STOCK")
            sistema.ver_alertas_stock()
            pausar()

        elif op == "7":
            break
        else:
            print("  Opcion invalida.")


# ── Modulo Pedidos ────────────────────────────────────────────────────────────

def flujo_crear_pedido(sistema):
    """Guia al usuario paso a paso en la creacion de un pedido personalizado."""
    header("NUEVO PEDIDO - DATOS DEL CLIENTE")

    nombre_cliente = pedir_no_vacio("  Nombre del cliente   : ")
    telefono       = pedir_telefono("  Telefono             : ")
    pais_destino   = pedir_no_vacio("  Pais de destino      : ")

    print("\n  Tamano del ramillete:")
    idx_tamano = seleccionar_opcion(TAMANOS)
    tamano     = TAMANOS[idx_tamano]

    # Seleccion de flores
    header("SELECCION DE FLORES")
    sistema.mostrar_inventario()

    items_solicitados = []
    while True:
        print("\n  Agregar flor al ramillete (Enter sin codigo para terminar):")
        codigo = input("  Codigo de la flor: ").strip().upper()
        if not codigo:
            if not items_solicitados:
                print("  Debe agregar al menos una flor al ramillete.")
                continue
            break
        flor = sistema.inventario.buscar(codigo)
        if flor is None:
            print(f"  Flor '{codigo}' no encontrada.")
            continue
        if flor.stock == 0:
            print(f"  '{flor.nombre} ({flor.color})' sin stock disponible.")
            continue
        print(f"  {flor.nombre} ({flor.color}) - Stock: {flor.stock} - ${flor.precio:.2f} c/u")
        cantidad = pedir_entero(f"  Cantidad (max {flor.stock}): ", minimo=1, maximo=flor.stock)
        items_solicitados.append((codigo, cantidad))
        print(f"  Agregado: {flor.nombre} ({flor.color}) x{cantidad}")

    # Resumen antes de confirmar
    print("\n  " + "─" * 50)
    print("  RESUMEN DEL PEDIDO:")
    print(f"  Cliente    : {nombre_cliente}")
    print(f"  Telefono   : {telefono}")
    print(f"  Destino    : {pais_destino}")
    print(f"  Tamano     : {tamano}")
    print("  Flores:")
    total_estimado = 0
    for cod, cant in items_solicitados:
        flor = sistema.inventario.buscar(cod)
        subtotal = flor.precio * cant
        total_estimado += subtotal
        print(f"    {flor.nombre} ({flor.color}) x{cant} = ${subtotal:.2f}")
    print(f"  TOTAL ESTIMADO: ${total_estimado:.2f}")
    print("  " + "─" * 50)

    confirmar = input("\n  Confirmar pedido? (s/n): ").strip().lower()
    if confirmar not in ("s", "si"):
        print("  Pedido cancelado.")
        return

    pedido = sistema.crear_pedido(nombre_cliente, telefono, pais_destino,
                                   tamano, items_solicitados)
    if pedido:
        print(pedido.resumen())
        print(f"\n  Pedido {pedido.id_pedido} registrado exitosamente.")


def menu_pedidos(sistema):
    while True:
        header("MODULO DE GESTION DE PEDIDOS")
        print("  1. Crear nuevo pedido")
        print("  2. Ver todos los pedidos")
        print("  3. Ver pedidos por estado")
        print("  4. Buscar pedido por ID")
        print("  5. Cambiar estado de un pedido")
        print("  6. Agregar notas a un pedido")
        print("  7. Eliminar pedido")
        print("  8. Volver al menu principal")
        op = input("\n  Seleccione una opcion: ").strip()

        if op == "1":
            flujo_crear_pedido(sistema)
            pausar()

        elif op == "2":
            header("TODOS LOS PEDIDOS")
            sistema.listar_pedidos()
            pausar()

        elif op == "3":
            header("PEDIDOS POR ESTADO")
            print("  Estados disponibles:")
            idx = seleccionar_opcion(ESTADOS_PEDIDO)
            estado = ESTADOS_PEDIDO[idx]
            header(f"PEDIDOS - {estado.upper()}")
            sistema.listar_pedidos(filtro_estado=estado)
            pausar()

        elif op == "4":
            header("BUSCAR PEDIDO")
            id_pedido = pedir_no_vacio("  ID del pedido (ej. P001): ").upper()
            pedido    = sistema.buscar_pedido(id_pedido)
            if pedido:
                print(pedido.resumen())
            else:
                print(f"  Pedido '{id_pedido}' no encontrado.")
            pausar()

        elif op == "5":
            header("CAMBIAR ESTADO")
            sistema.listar_pedidos()
            id_pedido = pedir_no_vacio("\n  ID del pedido: ").upper()
            pedido    = sistema.buscar_pedido(id_pedido)
            if pedido:
                print(f"  Estado actual: {pedido.estado}")
                print("  Nuevo estado:")
                idx        = seleccionar_opcion(ESTADOS_PEDIDO)
                nuevo_estado = ESTADOS_PEDIDO[idx]
                sistema.cambiar_estado_pedido(id_pedido, nuevo_estado)
            else:
                print(f"  Pedido '{id_pedido}' no encontrado.")
            pausar()

        elif op == "6":
            header("AGREGAR NOTAS")
            id_pedido = pedir_no_vacio("  ID del pedido: ").upper()
            notas     = pedir_no_vacio("  Notas        : ")
            sistema.modificar_notas_pedido(id_pedido, notas)
            pausar()

        elif op == "7":
            header("ELIMINAR PEDIDO")
            sistema.listar_pedidos()
            id_pedido = pedir_no_vacio("\n  ID del pedido a eliminar: ").upper()
            confirmar = input(f"  Confirmar eliminacion de {id_pedido}? (s/n): ").strip().lower()
            if confirmar in ("s", "si"):
                sistema.eliminar_pedido(id_pedido)
            else:
                print("  Operacion cancelada.")
            pausar()

        elif op == "8":
            break
        else:
            print("  Opcion invalida.")


# ── Modulo Logistica ──────────────────────────────────────────────────────────

def menu_logistica(sistema):
    while True:
        header("MODULO DE LOGISTICA Y ENVIOS")
        print("  1. Ver cola de envios")
        print("  2. Procesar siguiente envio (despachar)")
        print("  3. Ver pedidos listos para enviar")
        print("  4. Volver al menu principal")
        op = input("\n  Seleccione una opcion: ").strip()

        if op == "1":
            header("COLA DE ENVIOS")
            sistema.mostrar_cola_envios()
            pausar()

        elif op == "2":
            header("PROCESAR ENVIO")
            sistema.procesar_siguiente_envio()
            pausar()

        elif op == "3":
            header("PEDIDOS LISTOS PARA ENVIAR")
            sistema.listar_pedidos(filtro_estado="En preparacion")
            print("\n  Consejo: Cambie el estado a 'Enviado' para encolar en logistica.")
            pausar()

        elif op == "4":
            break
        else:
            print("  Opcion invalida.")


# ── Modulo Historial ──────────────────────────────────────────────────────────

def menu_historial(sistema):
    while True:
        header("HISTORIAL DE OPERACIONES")
        print("  1. Ver historial reciente")
        print("  2. Deshacer ultima accion")
        print("  3. Volver al menu principal")
        op = input("\n  Seleccione una opcion: ").strip()

        if op == "1":
            header("HISTORIAL")
            sistema.mostrar_historial(limite=20)
            pausar()

        elif op == "2":
            header("DESHACER")
            if not sistema.historial.esta_vacia():
                ultima = sistema.historial.peek()
                print(f"  Ultima accion: {ultima['accion']} | {ultima.get('timestamp','')}")
                confirmar = input("  Deshacer esta accion? (s/n): ").strip().lower()
                if confirmar in ("s", "si"):
                    sistema.deshacer()
                else:
                    print("  Operacion cancelada.")
            else:
                print("  No hay acciones para deshacer.")
            pausar()

        elif op == "3":
            break
        else:
            print("  Opcion invalida.")


# ── Menu principal ────────────────────────────────────────────────────────────

def main():
    sistema = SistemaFloraExport()

    print(f"\n  {SEP}")
    print(f"  {'SISTEMA DE GESTION DE PEDIDOS FLORAEXPORT'.center(56)}")
    print(f"  {SEP}")
    print(f"  Fecha: {datetime.now().strftime('%d/%m/%Y')} - "
          f"Hora: {datetime.now().strftime('%H:%M:%S')}")

    while True:
        print(f"\n  Seleccione un modulo:")
        print("  1. Modulo de Gestion de Pedidos")
        print("  2. Modulo de Inventario de Flores")
        print("  3. Modulo de Logistica y Envios")
        print("  4. Historial de Operaciones")
        print("  5. Salir")
        op = input("\n  Seleccione una opcion: ").strip()

        if op == "1":
            menu_pedidos(sistema)
        elif op == "2":
            menu_inventario(sistema)
        elif op == "3":
            menu_logistica(sistema)
        elif op == "4":
            menu_historial(sistema)
        elif op == "5":
            print(f"\n  {'─'*58}")
            print(f"  Gracias por usar FloraExport. Hasta pronto.")
            print(f"  {'─'*58}\n")
            break
        else:
            print("  Opcion invalida.")


if __name__ == "__main__":
    main()