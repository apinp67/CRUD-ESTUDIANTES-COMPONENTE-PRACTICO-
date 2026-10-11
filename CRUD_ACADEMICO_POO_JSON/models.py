"""Clases base: abstracción, encapsulamiento y herencia."""
from abc import ABC, abstractmethod

class ModeloBase(ABC):
    CAMPOS = ('id_registro',)
    def __init__(self, id_registro):
        self.__id_registro = int(id_registro)
        if self.__id_registro < 1:
            raise ValueError('El ID debe ser positivo')

    @property
    def id_registro(self):
        return self.__id_registro

    @staticmethod
    def limpiar(valor):
        return str(valor).strip()

    def a_diccionario(self):
        return {'id_registro': self.id_registro}

    @abstractmethod
    def etiqueta(self):
        pass

    def __str__(self):
        return f'[{self.id_registro}] {self.etiqueta()}'

class Persona(ModeloBase, ABC):
    CAMPOS = ModeloBase.CAMPOS + ('nombre', 'apellido', 'email')
    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    @property
    def nombre(self): return self.__nombre
    @nombre.setter
    def nombre(self, valor):
        valor = self.limpiar(valor)
        if not valor: raise ValueError('Nombre obligatorio')
        self.__nombre = valor.title()

    @property
    def apellido(self): return self.__apellido
    @apellido.setter
    def apellido(self, valor):
        valor = self.limpiar(valor)
        if not valor: raise ValueError('Apellido obligatorio')
        self.__apellido = valor.title()

    @property
    def email(self): return self.__email
    @email.setter
    def email(self, valor):
        valor = self.limpiar(valor).lower()
        if '@' not in valor or '.' not in valor.split('@')[-1]:
            raise ValueError('Correo electrónico inválido')
        self.__email = valor

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'

    def a_diccionario(self):
        return {**super().a_diccionario(), 'nombre': self.nombre,
                'apellido': self.apellido, 'email': self.email}
