"""Modelos académicos. Notas contenidas dentro de cada matrícula."""
from models import ModeloBase, Persona

class Estudiante(Persona):
    CAMPOS = Persona.CAMPOS + ('carnet',)
    def __init__(self, id_registro, nombre, apellido, email, carnet):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = carnet
    @property
    def carnet(self): return self.__carnet
    @carnet.setter
    def carnet(self, valor):
        valor = self.limpiar(valor).upper()
        if len(valor) < 4: raise ValueError('Carnet: mínimo 4 caracteres')
        self.__carnet = valor
    def a_diccionario(self):
        return {**super().a_diccionario(), 'carnet': self.carnet}
    def etiqueta(self):
        return f'{self.nombre_completo} | carnet {self.carnet}'

class Docente(Persona):
    CAMPOS = Persona.CAMPOS + ('titulo', 'especialidad')
    def __init__(self, id_registro, nombre, apellido, email, titulo='', especialidad=''):
        super().__init__(id_registro, nombre, apellido, email)
        self.titulo = titulo
        self.especialidad = especialidad
    @property
    def titulo(self): return self.__titulo
    @titulo.setter
    def titulo(self, valor): self.__titulo = self.limpiar(valor)
    @property
    def especialidad(self): return self.__especialidad
    @especialidad.setter
    def especialidad(self, valor): self.__especialidad = self.limpiar(valor)
    def a_diccionario(self):
        return {**super().a_diccionario(), 'titulo': self.titulo, 'especialidad': self.especialidad}
    def etiqueta(self):
        return f'{self.nombre_completo} | {self.especialidad or "Sin especialidad"}'

class Materia(ModeloBase):
    CAMPOS = ModeloBase.CAMPOS + ('nombre', 'codigo', 'creditos', 'docente_id')
    def __init__(self, id_registro, nombre, codigo, creditos, docente_id=0):
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = creditos
        self.docente_id = docente_id
    @property
    def nombre(self): return self.__nombre
    @nombre.setter
    def nombre(self, valor):
        valor = self.limpiar(valor)
        if not valor: raise ValueError('Nombre de materia obligatorio')
        self.__nombre = valor
    @property
    def codigo(self): return self.__codigo
    @codigo.setter
    def codigo(self, valor):
        valor = self.limpiar(valor).upper()
        if not valor: raise ValueError('Código obligatorio')
        self.__codigo = valor
    @property
    def creditos(self): return self.__creditos
    @creditos.setter
    def creditos(self, valor):
        valor = int(valor)
        if valor <= 0: raise ValueError('Créditos deben ser positivos')
        self.__creditos = valor
    @property
    def docente_id(self): return self.__docente_id
    @docente_id.setter
    def docente_id(self, valor):
        valor = int(valor)
        if valor < 0: raise ValueError('ID docente inválido')
        self.__docente_id = valor
    def a_diccionario(self):
        return {**super().a_diccionario(), 'nombre': self.nombre, 'codigo': self.codigo,
                'creditos': self.creditos, 'docente_id': self.docente_id}
    def etiqueta(self):
        return f'{self.codigo} | {self.nombre} | {self.creditos} créditos | docente {self.docente_id or "sin asignar"}'

class Nota:
    """Objeto compuesto: existe únicamente dentro de una matrícula."""
    def __init__(self, tipo, valor, peso=1):
        self.tipo = tipo
        self.valor = valor
        self.peso = peso
    @property
    def tipo(self): return self.__tipo
    @tipo.setter
    def tipo(self, valor):
        valor = str(valor).strip().lower()
        if not valor: raise ValueError('Tipo de nota obligatorio')
        self.__tipo = valor
    @property
    def valor(self): return self.__valor
    @valor.setter
    def valor(self, valor):
        valor = float(valor)
        if not 0 <= valor <= 20: raise ValueError('La nota debe estar entre 0 y 20')
        self.__valor = valor
    @property
    def peso(self): return self.__peso
    @peso.setter
    def peso(self, valor):
        valor = float(valor)
        if valor <= 0: raise ValueError('Peso debe ser positivo')
        self.__peso = valor
    def a_diccionario(self):
        return {'tipo': self.tipo, 'valor': self.valor, 'peso': self.peso}

class Matricula(ModeloBase):
    CAMPOS = ModeloBase.CAMPOS + ('estudiante_id', 'materia_id', 'periodo', 'notas')
    def __init__(self, id_registro, estudiante_id, materia_id, periodo, notas=None):
        super().__init__(id_registro)
        self.estudiante_id = estudiante_id
        self.materia_id = materia_id
        self.periodo = periodo
        self.__notas = []
        for nota in (notas or []):
            self.agregar_nota(**nota) if isinstance(nota, dict) else self.agregar_nota(nota.tipo, nota.valor, nota.peso)
    @property
    def estudiante_id(self): return self.__estudiante_id
    @estudiante_id.setter
    def estudiante_id(self, valor):
        valor = int(valor)
        if valor < 1: raise ValueError('Estudiante inválido')
        self.__estudiante_id = valor
    @property
    def materia_id(self): return self.__materia_id
    @materia_id.setter
    def materia_id(self, valor):
        valor = int(valor)
        if valor < 1: raise ValueError('Materia inválida')
        self.__materia_id = valor
    @property
    def periodo(self): return self.__periodo
    @periodo.setter
    def periodo(self, valor):
        valor = self.limpiar(valor)
        if not valor: raise ValueError('Periodo obligatorio')
        self.__periodo = valor
    @property
    def notas(self): return tuple(self.__notas)
    def agregar_nota(self, tipo, valor, peso=1):
        self.__notas.append(Nota(tipo, valor, peso))
    def quitar_nota(self, posicion):
        if not 1 <= posicion <= len(self.__notas): raise ValueError('Número de nota inexistente')
        self.__notas.pop(posicion - 1)
    @property
    def promedio(self):
        if not self.__notas: return None
        return sum(n.valor * n.peso for n in self.__notas) / sum(n.peso for n in self.__notas)
    @property
    def estado(self):
        if self.promedio is None: return 'Sin notas'
        return 'Aprobado' if self.promedio >= 14 else 'Reprobado'
    def a_diccionario(self):
        return {**super().a_diccionario(), 'estudiante_id': self.estudiante_id,
                'materia_id': self.materia_id, 'periodo': self.periodo,
                'notas': [n.a_diccionario() for n in self.__notas]}
    def etiqueta(self):
        promedio = f'{self.promedio:.2f}' if self.promedio is not None else '—'
        return f'Est. {self.estudiante_id} | materia {self.materia_id} | {self.periodo} | promedio {promedio} | {self.estado}'
