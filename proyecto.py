import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import os
from mutagen.mp3 import MP3

pygame.mixer.init()

class NodoCancion:
    def __init__(self, nombre, artista, duracion, ruta):
        self.nombre = nombre
        self.artista = artista
        self.duracion = duracion
        self.ruta = ruta
        self.siguiente = None
        self.anterior = None

class ListaReproduccion:
    def __init__(self):
        self.primero = None
        self.actual = None

    def agregar_cancion(self, nombre, artista, duracion, ruta):
        nuevo = NodoCancion(nombre, artista, duracion, ruta)
        if not self.primero:
            self.primero = nuevo
            self.primero.siguiente = self.primero.anterior = self.primero
        else:
            ultimo = self.primero.anterior
            ultimo.siguiente = nuevo
            nuevo.anterior = ultimo
            nuevo.siguiente = self.primero
            self.primero.anterior = nuevo
        self.actual = self.primero

    def eliminar_cancion_actual(self):
        if not self.actual:
            return
        if self.actual.siguiente == self.actual:
            self.primero = self.actual = None
        else:
            anterior = self.actual.anterior
            siguiente = self.actual.siguiente
            anterior.siguiente = siguiente
            siguiente.anterior = anterior
            if self.actual == self.primero:
                self.primero = siguiente
            self.actual = siguiente
