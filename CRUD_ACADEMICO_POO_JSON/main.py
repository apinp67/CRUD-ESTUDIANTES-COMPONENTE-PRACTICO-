"""Punto de entrada del programa: ejecutar con python main.py."""
from controllers import SistemaAcademico
from views import MenuCRUD, menu_matriculas, encabezado, opciones, aviso


def main():
    sistema = SistemaAcademico()
    menus = {
        '1': MenuCRUD('Estudiantes', sistema.estudiantes, sistema.eliminar_estudiante),
        '2': MenuCRUD('Docentes', sistema.docentes, sistema.eliminar_docente),
        '3': MenuCRUD('Materias', sistema.materias, sistema.eliminar_materia),
    }
    while True:
        encabezado('SISTEMA ACADÉMICO - POO Y JSON')
        opciones([
            ('1', 'Gestionar estudiantes'),
            ('2', 'Gestionar docentes'),
            ('3', 'Gestionar materias'),
            ('4', 'Gestionar matrículas y notas'),
            ('0', 'Salir del programa'),
        ])
        opcion = input('Seleccione una opción: ').strip()
        if opcion == '0':
            aviso('Hasta luego.')
            break
        if opcion in menus:
            menus[opcion].ejecutar()
        elif opcion == '4':
            menu_matriculas(sistema)
        else:
            aviso('Opción no válida. Intente nuevamente.')


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nPrograma finalizado.')
