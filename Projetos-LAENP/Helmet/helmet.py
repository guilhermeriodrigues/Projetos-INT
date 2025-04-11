import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageSequence
import mysql.connector
from mysql.connector import Error
from datetime import datetime

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sua_senha',
    'database': 'ensaios_capacetes'
}

def inserir_acelerometro(acel_x, acel_y, acel_z):
    """
    Insere os dados dos acelerômetros na tabela AcelerometroImpacto
    (no nosso modelo, estes dados estarão na tabela unificada com o ensaio de impacto).
    """
    try:
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()
        sql = """INSERT INTO AcelerometroImpacto (acel_x, acel_y, acel_z, tempo_amostra)
                 VALUES (%s, %s, %s, %s)"""
    
        tempo_amostra = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        valores = (acel_x, acel_y, acel_z, tempo_amostra)
        cursor.execute(sql, valores)
        conexao.commit()
        cursor.close()
        conexao.close()
        messagebox.showinfo("Sucesso", "Dados de acelerômetro salvos com sucesso!")
    except Error as e:
        messagebox.showerror("Erro no Banco", f"Erro ao inserir dados: {e}")


class ElevatorAdjustment(ttk.Frame):
    def _init_(self, master):
        super()._init_(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        self.step = 1
        self.position = tk.IntVar(value=0)
        
        ttk.Label(self, text="Ajuste Fino do Elevador", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        ttk.Label(self, text="Posição (mm):").grid(row=1, column=0, sticky="w")
        ttk.Label(self, textvariable=self.position).grid(row=1, column=1, sticky="w")
        
        ttk.Button(self, text="+1mm", command=self.increment).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self, text="-1mm", command=self.decrement).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self, text="Voltar", command=self.master.master.show_main_menu).grid(row=3, column=0, columnspan=2, pady=10)
    
    def increment(self):
        self.position.set(self.position.get() + self.step)
    
    def decrement(self):
        self.position.set(self.position.get() - self.step)

class FrictionSetting(ttk.Frame):
    def _init_(self, master):
        super()._init_(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Configuração do Atrito", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        
        self.friction = tk.DoubleVar()
        ttk.Label(self, text="Valor do Atrito:").grid(row=1, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.friction).grid(row=1, column=1, sticky="w")
        
        ttk.Button(self, text="Salvar", command=self.master.master.show_main_menu).grid(row=2, column=0, columnspan=2, pady=10)

class SensorCorrection(ttk.Frame):
    def _init_(self, master):
        super()._init_(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Correção dos Acelerômetros", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        
        self.correction_x = tk.DoubleVar()
        self.correction_y = tk.DoubleVar()
        self.correction_z = tk.DoubleVar()
        
        ttk.Label(self, text="Correção Canal X:").grid(row=1, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.correction_x).grid(row=1, column=1, sticky="w")
        ttk.Label(self, text="Correção Canal Y:").grid(row=2, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.correction_y).grid(row=2, column=1, sticky="w")
        ttk.Label(self, text="Correção Canal Z:").grid(row=3, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.correction_z).grid(row=3, column=1, sticky="w")
        
        ttk.Button(self, text="Aplicar", command=self.master.master.show_main_menu).grid(row=4, column=0, columnspan=2, pady=10)

class TestSetup(ttk.Frame):
    def _init_(self, master):
        super()._init_(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Configuração do Teste", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        
        ttk.Label(self, text="Escolha a base do ensaio:").grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(self, text="Plana", command=self.next_step).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self, text="Hemisférica", command=self.next_step).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self, text="Voltar", command=self.master.master.show_main_menu).grid(row=3, column=0, columnspan=2, pady=10)
    
    def next_step(self):
        self.master.master.load_content(TestRegistration)

class TestRegistration(ttk.Frame):
    def _init_(self, master):
        super()._init_(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Registro dos Dados", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        self.fields = ["Empresa", "Modelo do Capacete", "Número da Amostra", "Número do Procedimento/Relatório", 
                       "Posição do Ensaio", "Condicionamento", "Tamanho do Capacete", "Norma Utilizada"]
        self.entries = {}
        row = 1
        for field in self.fields:
            ttk.Label(self, text=field+":").grid(row=row, column=0, sticky="w", pady=2)
            entry = ttk.Entry(self)
            entry.grid(row=row, column=1, sticky="ew", pady=2)
            self.entries[field] = entry
            row += 1
        
        ttk.Button(self, text="Salvar", command=self.master.master.show_main_menu).grid(row=row, column=0, columnspan=2, pady=10)

class SensorMonitor(ttk.Frame):
    def _init_(self, master):
        super()._init_(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Monitoramento de Sensores", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        
        self.accel_mv = tk.DoubleVar()
        self.accel_g = tk.DoubleVar()
        
        ttk.Label(self, text="Sinal de mV/g do Acelerômetro:").grid(row=1, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.accel_mv, width=10).grid(row=1, column=1, sticky="w")
        ttk.Label(self, text="Canal X (mV):").grid(row=2, column=0, sticky="w")
        ttk.Label(self, textvariable=self.accel_mv).grid(row=2, column=1, sticky="w")
        ttk.Label(self, text="Canal X (g):").grid(row=3, column=0, sticky="w")
        ttk.Label(self, textvariable=self.accel_g).grid(row=3, column=1, sticky="w")
        
        
        self.image_label = ttk.Label(self)
        self.image_label.grid(row=4, column=0, columnspan=2, pady=10)
        self.display_gif("led_binary.gif")
        
       
        sensor_frame = ttk.LabelFrame(self, text="Sensores")
        sensor_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        self.sensor_vars = {}
        sensors = ["Sensor de Velocidade", "Garra da Coroa", "Porta", "Pistão da Corda"]
        col = 0
        row = 0
        for sensor in sensors:
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(sensor_frame, text=sensor, variable=var)
            chk.grid(row=row, column=col, padx=5, pady=5, sticky="w")
            self.sensor_vars[sensor] = var
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        
        ttk.Button(self, text="Iniciar Teste", command=self.iniciar_teste).grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(self, text="Voltar", command=self.master.master.show_main_menu).grid(row=7, column=0, columnspan=2, pady=10)
    
    def display_gif(self, filepath):
        try:
            self.gif = Image.open(filepath)
            self.frames = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(self.gif)]
            self.index = 0
            self.animate()
        except Exception as e:
            ttk.Label(self, text="Erro ao carregar imagem").grid(row=4, column=0, columnspan=2)
    
    def animate(self):
        self.image_label.config(image=self.frames[self.index])
        self.index = (self.index + 1) % len(self.frames)
        self.after(100, self.animate)
    
    def iniciar_teste(self):
        
        try:
            acel_x = float(self.accel_mv.get())
            acel_y = float(self.accel_g.get())  
            acel_z = 0.0  
        except ValueError:
            messagebox.showerror("Erro", "Insira valores numéricos válidos para os sensores.")
            return
        
        
        inserir_acelerometro(acel_x, acel_y, acel_z)
        
       
        self.master.master.load_content(TestSetup)

#

class AboutFrame(ttk.Frame):
    def _init_(self, master):
        super()._init_(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Sobre", font=('Helvetica', 14, 'bold')).grid(row=0, column=0, pady=(0,10))
        ttk.Label(self, text="Software de Ensaio de Capacete\nVersão 1.0\n© 2025 Sua Empresa").grid(row=1, column=0, pady=10)
        ttk.Button(self, text="Voltar", command=self.master.master.show_main_menu).grid(row=2, column=0, pady=10)

class EmpresaFrame(ttk.Frame):
    def _init_(self, master):
        super()._init_(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Dados da Empresa", font=('Helvetica', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        ttk.Label(self, text="Nome:").grid(row=1, column=0, sticky="w")
        self.entry_nome = ttk.Entry(self)
        self.entry_nome.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Cidade:").grid(row=2, column=0, sticky="w")
        self.entry_cidade = ttk.Entry(self)
        self.entry_cidade.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="País:").grid(row=3, column=0, sticky="w")
        self.entry_pais = ttk.Entry(self)
        self.entry_pais.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Estado:").grid(row=4, column=0, sticky="w")
        self.entry_estado = ttk.Entry(self)
        self.entry_estado.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="CNPJ:").grid(row=5, column=0, sticky="w")
        self.entry_cnpj = ttk.Entry(self)
        self.entry_cnpj.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Telefone:").grid(row=6, column=0, sticky="w")
        self.entry_telefone = ttk.Entry(self)
        self.entry_telefone.grid(row=6, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Email:").grid(row=7, column=0, sticky="w")
        self.entry_email = ttk.Entry(self)
        self.entry_email.grid(row=7, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(self, text="Salvar", command=self.master.master.show_main_menu).grid(row=8, column=0, columnspan=2, pady=10)

class CapacetesFrame(ttk.Frame):
    def _init_(self, master):
        super()._init_(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Cadastro de Capacetes", font=('Helvetica', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        ttk.Label(self, text="Modelo:").grid(row=1, column=0, sticky="w")
        self.entry_modelo = ttk.Entry(self)
        self.entry_modelo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Fabricante:").grid(row=2, column=0, sticky="w")
        self.entry_fabricante = ttk.Entry(self)
        self.entry_fabricante.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Tamanho:").grid(row=3, column=0, sticky="w")
        self.entry_tamanho = ttk.Entry(self)
        self.entry_tamanho.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(self, text="Salvar", command=self.master.master.show_main_menu).grid(row=4, column=0, columnspan=2, pady=10)



class MainApp(tk.Tk):
    def _init_(self):
        super()._init_()
        self.title("Software de Ensaio de Capacete")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        self.style.configure("TButton", font=("Helvetica", 10))
        
        # Área de navegação e conteúdo
        self.nav_frame = ttk.Frame(self, width=200, padding=10)
        self.nav_frame.grid(row=0, column=0, sticky="ns")
        self.content_frame = ttk.Frame(self, padding=10)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.create_navigation()
        self.show_main_menu()
    
    def create_navigation(self):
        ttk.Label(self.nav_frame, text="Menu", font=("Helvetica", 12, "bold")).grid(row=0, column=0, pady=10)
        nav_buttons = [
            ("Ajuste do Elevador", lambda: self.load_content(ElevatorAdjustment)),
            ("Configurar Atrito", lambda: self.load_content(FrictionSetting)),
            ("Monitorar Sensores", lambda: self.load_content(SensorMonitor)),
            ("Correção dos Acelerômetros", lambda: self.load_content(SensorCorrection)),
            ("Registro de Dados", lambda: self.load_content(TestRegistration)),
            ("Configuração do Teste", lambda: self.load_content(TestSetup)),
            ("Sobre", lambda: self.load_content(AboutFrame)),
            ("Empresa", lambda: self.load_content(EmpresaFrame)),
            ("Capacetes", lambda: self.load_content(CapacetesFrame))
        ]
        for idx, (text, command) in enumerate(nav_buttons, start=1):
            ttk.Button(self.nav_frame, text=text, command=command).grid(row=idx, column=0, pady=5, sticky="ew")
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def load_content(self, content_class):
        self.clear_content()
        content_class(self.content_frame)
    
    def show_main_menu(self):
        self.clear_content()
        welcome = ttk.Label(self.content_frame, text="Bem-vindo ao Software de Ensaio de Capacete", font=("Helvetica", 14))
        welcome.pack(expand=True)

if __name__ == "_main_":
    app = MainApp()
    app.mainloop()
