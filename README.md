# FloraExport - Sistema de Gestion de Pedidos

Sistema de gestion para una empresa exportadora de ramilletes de flores. Permite administrar el inventario, registrar pedidos de clientes, gestionar la logistica de envios y mantener un historial de operaciones con soporte de deshacer.

---

## Estructuras de datos utilizadas

| Estructura | Uso en el sistema |
|---|---|
| Lista Enlazada | Inventario de flores |
| Pila (LIFO) | Historial de operaciones y deshacer |
| Cola (FIFO) | Cola de envios en logistica |

---

## Modulos del sistema

**Inventario**
Ver, buscar y actualizar el catalogo de flores. Emite alertas cuando el stock baja de 30 unidades.

**Pedidos**
Crear pedidos por cliente, asignar flores del inventario, cambiar estado y eliminar pedidos pendientes.

**Logistica**
Administra la cola de envios. Los pedidos marcados como "Enviado" se encolan automaticamente y se despachan en orden de llegada.

**Historial**
Registra cada accion del sistema. Permite deshacer la ultima operacion realizada restaurando el estado anterior.

---

## Flujo de un pedido

```
Usuario crea pedido -> Sistema valida stock -> Pedido en estado Pendiente
-> En preparacion -> Enviado (entra a la cola) -> Despachado -> Entregado
```

---

## Inventario inicial

El sistema carga automaticamente 10 variedades de flores al iniciar:
Rosas (rojo, blanco, rosa), Tulipanes, Girasol, Orquideas, Clavel y Lirio.

---

## Requisitos

- Python 3.8 o superior
- No requiere librerias externas

## Ejecucion

```bash
python floraexport.py
```

---

## Limitaciones

- Los datos no se guardan al cerrar el programa (no hay persistencia en archivo o base de datos).
- Diseñado para uso en consola, sin interfaz grafica.
