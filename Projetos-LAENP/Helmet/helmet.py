import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
import threading

class ElevatorAdjustment(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Ajuste Fino do Elevador")
        self.geometry("300x150")
        
        self.step = 1
        self.position = tk.IntVar(value=0)
        
        ttk.Label(self, text="Posição (mm):").pack()
        ttk.Label(self, textvariable=self.position).pack()
        
        ttk.Button(self, text="+1mm", command=self.increment).pack()
        ttk.Button(self, text="-1mm", command=self.decrement).pack()
        
        ttk.Button(self, text="Cancelar", command=self.destroy).pack()
        ttk.Button(self, text="Continuar", command=self.destroy).pack()
    
    def increment(self):
        self.position.set(self.position.get() + self.step)
    
    def decrement(self):
        self.position.set(self.position.get() - self.step)

class FrictionSetting(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Configuração do Atrito")
        self.geometry("300x100")
        
        self.friction = tk.DoubleVar()
        ttk.Label(self, text="Valor do Atrito:").pack()
        ttk.Entry(self, textvariable=self.friction).pack()
        
        ttk.Button(self, text="Salvar", command=self.destroy).pack()

class SensorCorrection(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Correção dos Acelerômetros")
        self.geometry("300x200")
        
        self.correction_x = tk.DoubleVar()
        self.correction_y = tk.DoubleVar()
        self.correction_z = tk.DoubleVar()
        
        ttk.Label(self, text="Correção Canal X:").pack()
        ttk.Entry(self, textvariable=self.correction_x).pack()
        ttk.Label(self, text="Correção Canal Y:").pack()
        ttk.Entry(self, textvariable=self.correction_y).pack()
        ttk.Label(self, text="Correção Canal Z:").pack()
        ttk.Entry(self, textvariable=self.correction_z).pack()
        
        ttk.Button(self, text="Aplicar", command=self.destroy).pack()

class TestSetup(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Configuração do Teste")
        self.geometry("300x150")
        
        ttk.Label(self, text="Escolha a base do ensaio:").pack()
        ttk.Button(self, text="Plana", command=self.next_step).pack()
        ttk.Button(self, text="Hemisférica", command=self.next_step).pack()
    
    def next_step(self):
        TestRegistration(self)

class TestRegistration(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Registro dos Dados")
        self.geometry("400x400")
        
        self.fields = ["Empresa", "Modelo do Capacete", "Número da Amostra", "Número do Procedimento/Relatório", "Posição do Ensaio", "Condicionamento", "Tamanho do Capacete", "Norma Utilizada"]
        self.entries = {}
        
        for field in self.fields:
            ttk.Label(self, text=field).pack()
            entry = ttk.Entry(self)
            entry.pack()
            self.entries[field] = entry
        
        ttk.Button(self, text="Salvar", command=self.destroy).pack()

class SensorMonitor(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Monitoramento de Sensores")
        self.geometry("400x500")
        
        self.accel_mv = tk.DoubleVar()
        self.accel_g = tk.DoubleVar()
        
        ttk.Label(self, text="Sinal de mV/g do Acelerômetro:").pack()
        ttk.Entry(self, textvariable=self.accel_mv).pack()
        
        ttk.Label(self, text="Canal X (mV):").pack()
        ttk.Label(self, textvariable=self.accel_mv).pack()
        ttk.Label(self, text="Canal X (g):").pack()
        ttk.Label(self, textvariable=self.accel_g).pack()
        
        self.display_gif()
        
        self.create_sensor_controls()
        
        ttk.Button(self, text="Iniciar Teste", command=self.start_test).pack()
    
    def display_gif(self):
        self.image_label = ttk.Label(self)
        self.image_label.pack()
        
        self.gif = Image.open("led_binary.gif")
        self.frames = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(self.gif)]
        self.index = 0
        self.animate()
    
    def animate(self):
        self.image_label.config(image=self.frames[self.index])
        self.index = (self.index + 1) % len(self.frames)
        self.after(100, self.animate)
    
    def create_sensor_controls(self):
        self.sensors = ["Sensor de Velocidade", "Garra da Coroa", "Porta", "Pistão da Corda"]
        self.sensor_vars = {}
        
        for sensor in self.sensors:
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(self, text=sensor, variable=var)
            chk.pack()
            self.sensor_vars[sensor] = var
    
    def start_test(self):
        TestSetup(self)

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Software de Ensaio de Capacete")
        self.geometry("300x200")
        
        ttk.Button(self, text="Ajuste Fino do Elevador", command=self.open_elevator).pack()
        ttk.Button(self, text="Configurar Atrito", command=self.open_friction).pack()
        ttk.Button(self, text="Monitoramento de Sensores", command=self.open_sensors).pack()
        ttk.Button(self, text="Correção dos Acelerômetros", command=self.open_correction).pack()
    
    def open_elevator(self):
        ElevatorAdjustment(self)
    
    def open_friction(self):
        FrictionSetting(self)
    
    def open_sensors(self):
        SensorMonitor(self)
    
    def open_correction(self):
        SensorCorrection(self)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
