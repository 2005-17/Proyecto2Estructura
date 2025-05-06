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
            
    def avanzar(self):
        if self.actual:
            self.actual = self.actual.siguiente

    def retroceder(self):
        if self.actual:
            self.actual = self.actual.anterior

    def mostrar_lista(self):
        canciones = []
        if not self.primero:
            return canciones
        nodo = self.primero
        while True:
            canciones.append(f"{nodo.nombre} - {nodo.artista}")
            nodo = nodo.siguiente
            if nodo == self.primero:
                break
        return canciones

class ReproductorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎶 Reproductor de Música")
        self.root.geometry("420x620")
        self.root.configure(bg="#DCD0FF")
        self.lista = ListaReproduccion()
        self.en_pausa = False
        self.tiempo_actual = 0
        self.total_duracion = 0
        self.actualizando = False

        self.label_cancion = tk.Label(root, text="No hay canción seleccionada", wraplength=380,
                                      bg="#DCD0FF", fg="#3D3D3D", font=("Helvetica", 12, "bold"))
        self.label_cancion.pack(pady=10)

        self.lista_box = tk.Listbox(root, width=50, bg="#F2E9FF", fg="#3D3D3D",
                                    font=("Arial", 10), relief="flat", bd=2,
                                    highlightbackground="#BBA0FF", highlightthickness=2)
        self.lista_box.pack(pady=10)

        self.label_tiempo = tk.Label(root, text="00:00 / 00:00", bg="#DCD0FF", font=("Arial", 10, "bold"))
        self.label_tiempo.pack()

        self.barra_progreso = tk.Scale(root, from_=0, to=100, orient="horizontal",
                                       length=300, showvalue=0, bg="#DCD0FF",
                                       troughcolor="#A593E0", sliderrelief="raised",
                                       command=self.mover_barra)
        self.barra_progreso.pack(pady=5)

        self.botones_frame = tk.Frame(root, bg="#DCD0FF")
        self.botones_frame.pack(pady=10)

        self.btn_cargar = self.crear_boton("🎵 Cargar Canción", self.cargar_cancion, 0, 0)
        self.btn_play = self.crear_boton("▶️ Reproducir", self.reproducir, 0, 1)
        self.btn_pausa = self.crear_boton("⏸️ Pausar", self.pausar_reanudar, 1, 0)
        self.btn_detener = self.crear_boton("⏹️ Detener", self.detener, 1, 1)
        self.btn_ant = self.crear_boton("⏮️ Anterior", self.anterior, 2, 0)
        self.btn_sig = self.crear_boton("⏭️ Siguiente", self.siguiente, 2, 1)
        self.btn_eliminar = self.crear_boton("🗑️ Eliminar", self.eliminar_cancion, 3, 0)

    def crear_boton(self, texto, comando, fila, columna):
        boton = tk.Button(self.botones_frame, text=texto, command=comando,
                          bg="#A593E0", fg="white", font=("Arial", 11, "bold"),
                          activebackground="#8B78C6", relief="raised", bd=3,
                          width=18, height=2)
        boton.grid(row=fila, column=columna, padx=5, pady=5)
        return boton

    def cargar_cancion(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos MP3", "*.mp3")])
        if ruta:
            nombre_archivo = os.path.basename(ruta)
            try:
                duracion = int(MP3(ruta).info.length)
            except:
                duracion = 0
            self.lista.agregar_cancion(nombre_archivo, "Desconocido", duracion, ruta)
            self.actualizar_lista()

    def actualizar_lista(self):
        self.lista_box.delete(0, tk.END)
        for c in self.lista.mostrar_lista():
            self.lista_box.insert(tk.END, c)

    def reproducir(self):
        if self.lista.actual:
            try:
                pygame.mixer.music.load(self.lista.actual.ruta)
                pygame.mixer.music.play()
                self.label_cancion.config(text=f"🎧 Reproduciendo: {self.lista.actual.nombre}")
                self.en_pausa = False
                self.btn_pausa.config(text="⏸️ Pausar")
                self.tiempo_actual = 0
                self.total_duracion = self.lista.actual.duracion
                self.barra_progreso.config(to=self.total_duracion)
                if not self.actualizando:
                    self.actualizar_progreso()
            except:
                messagebox.showerror("Error", "No se pudo reproducir la canción.")

    def actualizar_progreso(self):
        if pygame.mixer.music.get_busy() and not self.en_pausa:
            self.tiempo_actual += 1
            if self.tiempo_actual <= self.total_duracion:
                self.barra_progreso.set(self.tiempo_actual)
                self.label_tiempo.config(text=f"{self.formato_tiempo(self.tiempo_actual)} / {self.formato_tiempo(self.total_duracion)}")
        self.root.after(1000, self.actualizar_progreso)
        self.actualizando = True

    def mover_barra(self, valor):
        valor = int(valor)
        if pygame.mixer.music.get_busy() or self.en_pausa:
            pygame.mixer.music.play(start=valor)
            self.tiempo_actual = valor
            self.en_pausa = False
            self.btn_pausa.config(text="⏸️ Pausar")
            self.label_tiempo.config(text=f"{self.formato_tiempo(valor)} / {self.formato_tiempo(self.total_duracion)}")

