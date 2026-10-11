"""Menús de consola del sistema académico. La lógica CRUD está en controllers.py."""

ANCHO = 54


def encabezado(titulo):
    print('\n' + '=' * ANCHO)
    print(titulo.upper().center(ANCHO))
    print('=' * ANCHO)


def opciones(items):
    for numero, descripcion in items:
        print(f'  {numero}. {descripcion}')
    print('-' * ANCHO)


def aviso(mensaje):
    print('\n' + '-' * ANCHO)
    print(mensaje)
    print('-' * ANCHO)


def mostrar_registros(registros, vacio='No hay registros disponibles.'):
    if not registros:
        aviso(vacio)
        return
    print('\n' + '-' * ANCHO)
    for indice, registro in enumerate(registros, 1):
        print(f'  {indice:>2}) {registro}')
    print('-' * ANCHO)
    print(f'Total de registros: {len(registros)}')


def pedir_entero(texto):
    return int(input(texto).strip())


def campos_nuevo(controlador):
    return [c for c in controlador.MODELO.CAMPOS if c != 'id_registro' and c != 'notas']


def pedir_datos(controlador, actual=None):
    datos = {}
    print('\n' + '-' * ANCHO)
    print('INGRESO DE DATOS' if actual is None else 'ACTUALIZACIÓN DE DATOS')
    print('-' * ANCHO)
    for campo in campos_nuevo(controlador):
        previo = getattr(actual, campo) if actual is not None else None
        aclaracion = f' [{previo}]' if actual is not None else ''
        nombre_campo = campo.replace('_', ' ').capitalize()
        entrada = input(f'{nombre_campo}{aclaracion}: ').strip()
        if actual is not None and entrada == '':
            continue
        if actual is None and campo == 'docente_id' and entrada == '':
            entrada = '0'
        datos[campo] = entrada
    return datos


class MenuCRUD:
    def __init__(self, titulo, controlador, al_eliminar=None):
        self.titulo, self.controlador = titulo, controlador
        self.al_eliminar = al_eliminar or controlador.eliminar

    def ejecutar(self):
        entidad = self.titulo.lower().rstrip('s')
        while True:
            encabezado('MENÚ DE ' + self.titulo)
            opciones([
                ('1', 'Crear ' + entidad),
                ('2', 'Listar ' + self.titulo.lower()),
                ('3', 'Consultar por ID'),
                ('4', 'Buscar ' + entidad),
                ('5', 'Actualizar ' + entidad),
                ('6', 'Eliminar ' + entidad),
                ('0', 'Regresar al menú principal'),
            ])
            op = input('Seleccione una opción: ').strip()
            if op == '0':
                return
            try:
                if op == '1':
                    obj = self.controlador.crear(pedir_datos(self.controlador))
                    aviso(f'Registro guardado correctamente:\n{obj}')
                elif op == '2':
                    encabezado('LISTADO DE ' + self.titulo)
                    mostrar_registros(self.controlador.listar())
                elif op == '3':
                    obj = self.controlador.obtener(pedir_entero('Ingrese el ID: '))
                    aviso(str(obj) if obj else 'Registro no encontrado.')
                elif op == '4':
                    texto = input('Ingrese el texto a buscar: ').strip()
                    mostrar_registros(self.controlador.buscar(texto), 'No se encontraron coincidencias.')
                elif op == '5':
                    id_ = pedir_entero('ID del registro a actualizar: ')
                    actual = self.controlador.obtener(id_)
                    if not actual:
                        raise ValueError('Registro no encontrado.')
                    print('Deje un campo vacío para conservar su valor actual.')
                    obj = self.controlador.actualizar(id_, pedir_datos(self.controlador, actual))
                    aviso(f'Registro actualizado correctamente:\n{obj}')
                elif op == '6':
                    id_ = pedir_entero('ID del registro a eliminar: ')
                    if input('¿Confirmar eliminación? (s/n): ').strip().lower() == 's':
                        self.al_eliminar(id_)
                        aviso('Registro eliminado correctamente.')
                    else:
                        aviso('Eliminación cancelada.')
                else:
                    aviso('Opción no válida. Intente nuevamente.')
            except (ValueError, TypeError) as error:
                aviso(f'Error: {error}')


def menu_matriculas(sistema):
    m = sistema.matriculas
    while True:
        encabezado('MENÚ DE MATRÍCULAS Y NOTAS')
        opciones([
            ('1', 'Crear matrícula'),
            ('2', 'Listar matrículas'),
            ('3', 'Consultar matrícula por ID'),
            ('4', 'Buscar matrícula'),
            ('5', 'Actualizar matrícula'),
            ('6', 'Eliminar matrícula'),
            ('7', 'Agregar nota'),
            ('8', 'Quitar nota'),
            ('9', 'Ver boletín de notas'),
            ('0', 'Regresar al menú principal'),
        ])
        op = input('Seleccione una opción: ').strip()
        if op == '0':
            return
        try:
            if op == '1':
                aviso(f'Matrícula guardada correctamente:\n{m.crear(pedir_datos(m))}')
            elif op == '2':
                encabezado('LISTADO DE MATRÍCULAS')
                mostrar_registros(m.listar(), 'No hay matrículas registradas.')
            elif op == '3':
                obj = m.obtener(pedir_entero('Ingrese el ID de la matrícula: '))
                aviso(str(obj) if obj else 'Matrícula no encontrada.')
            elif op == '4':
                texto = input('Ingrese el texto a buscar: ').strip()
                mostrar_registros(m.buscar(texto), 'No se encontraron coincidencias.')
            elif op == '5':
                id_ = pedir_entero('ID de la matrícula a actualizar: ')
                actual = m.obtener(id_)
                if not actual:
                    raise ValueError('No existe esa matrícula.')
                print('Deje los campos vacíos para conservar sus valores actuales.')
                aviso(f'Matrícula actualizada correctamente:\n{m.actualizar(id_, pedir_datos(m, actual))}')
            elif op == '6':
                id_ = pedir_entero('ID de la matrícula a eliminar: ')
                if input('¿Eliminar matrícula y todas sus notas? (s/n): ').strip().lower() == 's':
                    m.eliminar(id_)
                    aviso('Matrícula eliminada correctamente.')
                else:
                    aviso('Eliminación cancelada.')
            elif op == '7':
                encabezado('AGREGAR NOTA')
                id_ = pedir_entero('ID de la matrícula: ')
                tipo = input('Tipo (deber/lección/examen): ').strip()
                valor = input('Nota (0 a 20): ').strip()
                peso = input('Peso [1]: ').strip() or '1'
                m.agregar_nota(id_, tipo, valor, peso)
                aviso('Nota agregada correctamente.')
            elif op == '8':
                encabezado('QUITAR NOTA')
                id_ = pedir_entero('ID de la matrícula: ')
                print('\n' + str(m.boletin(id_)))
                m.quitar_nota(id_, pedir_entero('Número de nota a quitar: '))
                aviso('Nota eliminada correctamente.')
            elif op == '9':
                encabezado('BOLETÍN DE NOTAS')
                aviso(str(m.boletin(pedir_entero('ID de la matrícula: '))))
            else:
                aviso('Opción no válida. Intente nuevamente.')
        except (ValueError, TypeError) as error:
            aviso(f'Error: {error}')
