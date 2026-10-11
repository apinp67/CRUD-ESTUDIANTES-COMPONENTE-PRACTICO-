"""Controladores CRUD genéricos y validaciones por entidad."""
from abc import ABC, abstractmethod
from pathlib import Path
import json
from models_academico import Estudiante, Docente, Materia, Matricula

DATOS = Path(__file__).resolve().parent / 'datos'

class CrudBase(ABC):
    MODELO = None
    ARCHIVO = ''
    def __init__(self, carpeta=None):
        ruta = Path(carpeta) if carpeta else DATOS
        ruta.mkdir(parents=True, exist_ok=True)
        self.ruta = ruta / self.ARCHIVO
        if not self.ruta.exists(): self.ruta.write_text('[]\n', encoding='utf-8')

    def listar(self):
        try:
            datos = json.loads(self.ruta.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ValueError(f'Archivo JSON dañado: {self.ruta.name}') from error
        if not isinstance(datos, list): raise ValueError('El JSON debe contener una lista')
        return [self.MODELO(**registro) for registro in datos]

    def guardar(self, objetos):
        # Reemplazo temporal para no dejar JSON incompleto si se interrumpe la escritura.
        temporal = self.ruta.with_suffix('.tmp')
        temporal.write_text(json.dumps([o.a_diccionario() for o in objetos], ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temporal.replace(self.ruta)

    def obtener(self, identificador):
        return next((o for o in self.listar() if o.id_registro == int(identificador)), None)

    def buscar(self, texto):
        return [o for o in self.listar() if str(texto).casefold() in o.etiqueta().casefold()]

    @abstractmethod
    def validar(self, objeto, existentes):
        pass

    def crear(self, datos):
        objetos = self.listar()
        nuevo_id = max((o.id_registro for o in objetos), default=0) + 1
        obj = self.MODELO(id_registro=nuevo_id, **datos)
        self.validar(obj, objetos)
        self.guardar(objetos + [obj])
        return obj

    def actualizar(self, identificador, cambios):
        objetos = self.listar()
        anterior = next((o for o in objetos if o.id_registro == int(identificador)), None)
        if anterior is None: raise ValueError('Registro no encontrado')
        datos = anterior.a_diccionario()
        if 'id_registro' in cambios: raise ValueError('No se puede modificar el ID')
        datos.update(cambios)
        nuevo = self.MODELO(**datos)
        self.validar(nuevo, [o for o in objetos if o.id_registro != int(identificador)])
        self.guardar([nuevo if o.id_registro == int(identificador) else o for o in objetos])
        return nuevo

    def eliminar(self, identificador):
        objetos = self.listar()
        nuevos = [o for o in objetos if o.id_registro != int(identificador)]
        if len(objetos) == len(nuevos): raise ValueError('Registro no encontrado')
        self.guardar(nuevos)

class EstudianteController(CrudBase):
    MODELO, ARCHIVO = Estudiante, 'estudiantes.json'
    def validar(self, objeto, existentes):
        if any(o.carnet == objeto.carnet for o in existentes): raise ValueError('Carnet duplicado')
        if any(o.email == objeto.email for o in existentes): raise ValueError('Correo duplicado')

class DocenteController(CrudBase):
    MODELO, ARCHIVO = Docente, 'docentes.json'
    def validar(self, objeto, existentes):
        if any(o.email == objeto.email for o in existentes): raise ValueError('Correo duplicado')

class MateriaController(CrudBase):
    MODELO, ARCHIVO = Materia, 'materias.json'
    def __init__(self, docentes, carpeta=None):
        super().__init__(carpeta)
        self.docentes = docentes
    def validar(self, objeto, existentes):
        if any(o.codigo == objeto.codigo for o in existentes): raise ValueError('Código duplicado')
        if objeto.docente_id and not self.docentes.obtener(objeto.docente_id):
            raise ValueError('El docente asignado no existe')

class MatriculaController(CrudBase):
    MODELO, ARCHIVO = Matricula, 'matriculas.json'
    def __init__(self, estudiantes, materias, carpeta=None):
        super().__init__(carpeta)
        self.estudiantes, self.materias = estudiantes, materias
    def validar(self, objeto, existentes):
        if not self.estudiantes.obtener(objeto.estudiante_id): raise ValueError('Estudiante no existe')
        if not self.materias.obtener(objeto.materia_id): raise ValueError('Materia no existe')
        if any((o.estudiante_id, o.materia_id, o.periodo.casefold()) ==
               (objeto.estudiante_id, objeto.materia_id, objeto.periodo.casefold()) for o in existentes):
            raise ValueError('El estudiante ya está matriculado en esa materia y periodo')
    def agregar_nota(self, id_matricula, tipo, valor, peso=1):
        matricula = self.obtener(id_matricula)
        if not matricula: raise ValueError('Matrícula no encontrada')
        matricula.agregar_nota(tipo, valor, peso)
        self.actualizar(id_matricula, {'notas': [n.a_diccionario() for n in matricula.notas]})
    def quitar_nota(self, id_matricula, posicion):
        matricula = self.obtener(id_matricula)
        if not matricula: raise ValueError('Matrícula no encontrada')
        matricula.quitar_nota(posicion)
        self.actualizar(id_matricula, {'notas': [n.a_diccionario() for n in matricula.notas]})
    def boletin(self, id_matricula):
        m = self.obtener(id_matricula)
        if not m: raise ValueError('Matrícula no encontrada')
        est = self.estudiantes.obtener(m.estudiante_id)
        mat = self.materias.obtener(m.materia_id)
        lineas = [f'BOLETÍN | Matrícula {m.id_registro}',
                  f'Estudiante: {est.nombre_completo if est else "No disponible"}',
                  f'Materia: {mat.nombre if mat else "No disponible"}', f'Periodo: {m.periodo}', 'Notas:']
        lineas += [f'  {i}. {n.tipo}: {n.valor:.2f} (peso {n.peso:g})' for i, n in enumerate(m.notas, 1)]
        if not m.notas: lineas.append('  Sin notas')
        lineas.append(f'Promedio: {m.promedio:.2f}' if m.promedio is not None else 'Promedio: sin notas')
        lineas.append(f'Estado: {m.estado}')
        return '\n'.join(lineas)

class SistemaAcademico:
    def __init__(self, carpeta=None):
        self.estudiantes = EstudianteController(carpeta)
        self.docentes = DocenteController(carpeta)
        self.materias = MateriaController(self.docentes, carpeta)
        self.matriculas = MatriculaController(self.estudiantes, self.materias, carpeta)

    def eliminar_estudiante(self, identificador):
        if any(m.estudiante_id == int(identificador) for m in self.matriculas.listar()):
            raise ValueError('No se puede eliminar: tiene matrículas')
        self.estudiantes.eliminar(identificador)

    def eliminar_docente(self, identificador):
        if any(m.docente_id == int(identificador) for m in self.materias.listar()):
            raise ValueError('No se puede eliminar: tiene materias asignadas')
        self.docentes.eliminar(identificador)

    def eliminar_materia(self, identificador):
        if any(m.materia_id == int(identificador) for m in self.matriculas.listar()):
            raise ValueError('No se puede eliminar: tiene matrículas')
        self.materias.eliminar(identificador)
