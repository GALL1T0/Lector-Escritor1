import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread, Semaphore
import time

# Semáforos
mutex = Semaphore(1)
write = Semaphore(1)

# Contador de lectores
readcount = 0

class ProcessWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.title("Proceso")
        self.create_widgets()

    def create_widgets(self):
        self.text = tk.Text(self)
        self.text.pack()

        frame = ttk.Frame(self)
        frame.pack()

        self.read_button = ttk.Button(frame, text="Leer", command=self.read)
        self.read_button.pack(side="left")

        self.edit_button = ttk.Button(frame, text="Editar", command=self.edit)
        self.edit_button.pack(side="left")

        self.save_button = ttk.Button(frame, text="Guardar", command=self.save)
        self.save_button.pack(side="left")

    def read(self):
        def reader():
            global readcount
            mutex.acquire()
            readcount += 1
            if readcount == 1:
                if not write.acquire(blocking=False):
                    messagebox.showwarning("Advertencia", "Un escritor está escribiendo en el archivo.")
                    readcount -= 1
                    mutex.release()
                    return
            mutex.release()

            # Leer archivo
            with open('file.txt', 'r') as f:
                content = f.read()

            # Simular lectura en tiempo real
            for word in content.split():
                self.text.insert('end', word + ' ')
                self.text.update()
                time.sleep(0.5)

            mutex.acquire()
            readcount -= 1
            if readcount == 0:
                write.release()
            mutex.release()

        Thread(target=reader).start()

    def edit(self):
        self.text.delete('1.0', 'end')

    def save(self):
        def writer():
            if not write.acquire(blocking=False):
                messagebox.showwarning("Advertencia", "Otro escritor está escribiendo en el archivo.")
                return

            # Guardar archivo
            with open('file.txt', 'w') as f:
                f.write(self.text.get('1.0', 'end'))

            write.release()

        Thread(target=writer).start()

root = tk.Tk()
root.withdraw()

for _ in range(3):
    ProcessWindow(root)

root.mainloop()
