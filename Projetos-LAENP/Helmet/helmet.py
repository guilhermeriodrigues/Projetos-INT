import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageSequence
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Configurações do banco de dados MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '30746170',
    'database': 'ensaios_capacete'
}

# Funções de inserção no banco de dados

def inserir_acelerometro(acel_x, acel_y, acel_z):
    """
    Insere os dados dos acelerômetros na tabela AcelerometroImpacto
    (Nesta versão, fundimos os dados dos acelerômetros na tabela EnsaioImpacto).
    """
    try:
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()
        sql = """UPDATE EnsaioImpacto 
                 SET acel_x = %s, acel_y = %s, acel_z = %s, tempo_amostra = %s 
                 WHERE id_ensaio = (SELECT MAX(id_ensaio) FROM Ensaio)"""
        tempo_amostra = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        valores = (acel_x, acel_y, acel_z, tempo_amostra)
        cursor.execute(sql, valores)
        conexao.commit()
        cursor.close()
        conexao.close()
        messagebox.showinfo("Sucesso", "Dados dos acelerômetros salvos com sucesso!")
    except Error as e:
        messagebox.showerror("Erro no Banco", f"Erro ao inserir dados dos acelerômetros: {e}")

def inserir_empresa(nome, cidade, pais, estado, cnpj, telefone, email):
    """
    Insere os dados da Empresa na tabela Empresa.
    """
    try:
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()
        sql = """INSERT INTO Empresa (nome, cidade, pais, estado, cnpj, telefone, email)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        valores = (nome, cidade, pais, estado, cnpj, telefone, email)
        cursor.execute(sql, valores)
        conexao.commit()
        cursor.close()
        conexao.close()
        messagebox.showinfo("Sucesso", "Empresa cadastrada com sucesso!")
    except Error as e:
        messagebox.showerror("Erro no Banco", f"Erro ao cadastrar empresa: {e}")

def inserir_contrato(id_empresa, data_contrato, prazo, valor_servico, data_contato):
    """
    Insere os dados de Contrato na tabela Contrato.
    """
    try:
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()
        sql = """INSERT INTO Contrato (id_empresa, data_contrato, prazo, valor_servico, data_contato)
                 VALUES (%s, %s, %s, %s, %s)"""
        valores = (id_empresa, data_contrato, prazo, valor_servico, data_contato)
        cursor.execute(sql, valores)
        conexao.commit()
        cursor.close()
        conexao.close()
        messagebox.showinfo("Sucesso", "Contrato cadastrado com sucesso!")
    except Error as e:
        messagebox.showerror("Erro no Banco", f"Erro ao cadastrar contrato: {e}")

def inserir_relatorio(ensaio_id, texto_relatorio):
    """
    Insere os dados do relatório final na tabela Relatorio.
    """
    try:
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()
        sql = """INSERT INTO Relatorio (id_ensaio, texto_relatorio)
                 VALUES (%s, %s)"""
        valores = (ensaio_id, texto_relatorio)
        cursor.execute(sql, valores)
        conexao.commit()
        cursor.close()
        conexao.close()
        messagebox.showinfo("Sucesso", "Relatório salvo com sucesso!")
    except Error as e:
        messagebox.showerror("Erro no Banco", f"Erro ao salvar relatório: {e}")

def inserir_saidaDigital(ensaio_id, canal, valor, tempo_ativacao):
    """
    Insere os dados de saída digital na tabela SaidaDigital.
    """
    try:
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()
        sql = """INSERT INTO SaidaDigital (id_ensaio, canal, valor, tempo_ativacao)
                 VALUES (%s, %s, %s, %s)"""
        valores = (ensaio_id, canal, valor, tempo_ativacao)
        cursor.execute(sql, valores)
        conexao.commit()
        cursor.close()
        conexao.close()
        messagebox.showinfo("Sucesso", "Saída digital cadastrada!")
    except Error as e:
        messagebox.showerror("Erro no Banco", f"Erro ao salvar saída digital: {e}")


# ===========================#
# Interfaces (Frames) de Funcionalidade
# ===========================#

class ElevatorAdjustment(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
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
    def __init__(self, master):
        super().__init__(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Configuração do Atrito", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        self.friction = tk.DoubleVar()
        ttk.Label(self, text="Valor do Atrito:").grid(row=1, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.friction).grid(row=1, column=1, sticky="w")
        ttk.Button(self, text="Salvar", command=self.master.master.show_main_menu).grid(row=2, column=0, columnspan=2, pady=10)

class SensorCorrection(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
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
    def __init__(self, master):
        super().__init__(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Configuração do Teste", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        ttk.Label(self, text="Escolha a base do ensaio:").grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(self, text="Plana", command=self.next_step).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self, text="Hemisférica", command=self.next_step).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self, text="Voltar", command=self.master.master.show_main_menu).grid(row=3, column=0, columnspan=2, pady=10)
    
    def next_step(self):
        self.master.master.load_content(TestRegistration)

class TestRegistration(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Registro dos Dados", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        # Campos que serão persistidos na tabela EnsaioImpacto
        self.fields = ["Empresa", "Modelo do Capacete", "Número da Amostra", "Número do Procedimento/Relatório", 
                       "Posição do Ensaio", "Condicionamento", "Norma Utilizada"]
        self.entries = {}
        row = 1
        for field in self.fields:
            ttk.Label(self, text=f"{field}:").grid(row=row, column=0, sticky="w", pady=2)
            entry = ttk.Entry(self)
            entry.grid(row=row, column=1, sticky="ew", pady=2)
            self.entries[field] = entry
            row += 1
        ttk.Button(self, text="Salvar", command=self.master.master.show_main_menu).grid(row=row, column=0, columnspan=2, pady=10)

class SensorMonitor(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Monitoramento de Sensores", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        
        # Entradas para aceleração (mV/g) dos três eixos
        ttk.Label(self, text="Aceleração X (mV/g):").grid(row=1, column=0, sticky="w")
        self.entry_acel_x = ttk.Entry(self, width=10)
        self.entry_acel_x.grid(row=1, column=1, sticky="w")
        
        ttk.Label(self, text="Aceleração Y (mV/g):").grid(row=2, column=0, sticky="w")
        self.entry_acel_y = ttk.Entry(self, width=10)
        self.entry_acel_y.grid(row=2, column=1, sticky="w")
        
        ttk.Label(self, text="Aceleração Z (mV/g):").grid(row=3, column=0, sticky="w")
        self.entry_acel_z = ttk.Entry(self, width=10)
        self.entry_acel_z.grid(row=3, column=1, sticky="w")
        
        # Área para exibição do GIF animado
        self.image_label = ttk.Label(self)
        self.image_label.grid(row=4, column=0, columnspan=2, pady=10)
        self.display_gif("led_binary.gif")
        
        # Área de sensores extras
        sensor_frame = ttk.LabelFrame(self, text="Sensores Extras")
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
            self.frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(self.gif)]
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
            acel_x = float(self.entry_acel_x.get())
            acel_y = float(self.entry_acel_y.get())
            acel_z = float(self.entry_acel_z.get())
        except ValueError:
            messagebox.showerror("Erro", "Insira valores numéricos válidos para os acelerômetros.")
            return
        inserir_acelerometro(acel_x, acel_y, acel_z)
        self.master.master.load_content(TestSetup)

# Novas telas para dados que ainda não estão presentes na versão anterior

class AboutFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Sobre", font=('Helvetica', 14, 'bold')).grid(row=0, column=0, pady=(0,10))
        ttk.Label(self, text="Software de Ensaio de Capacete\nVersão 1.0\n© 2025 Sua Empresa").grid(row=1, column=0, pady=10)
        ttk.Button(self, text="Voltar", command=self.master.master.show_main_menu).grid(row=2, column=0, pady=10)

class EmpresaFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Cadastro de Empresa", font=('Helvetica', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
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
        ttk.Button(self, text="Salvar", command=self.salvar_empresa).grid(row=8, column=0, columnspan=2, pady=10)
    
    def salvar_empresa(self):
        nome = self.entry_nome.get()
        cidade = self.entry_cidade.get()
        pais = self.entry_pais.get()
        estado = self.entry_estado.get()
        cnpj = self.entry_cnpj.get()
        telefone = self.entry_telefone.get()
        email = self.entry_email.get()
        if not nome:
            messagebox.showerror("Erro", "O campo Nome é obrigatório.")
            return
        inserir_empresa(nome, cidade, pais, estado, cnpj, telefone, email)
        self.master.master.show_main_menu()

class CapacetesFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
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
        ttk.Button(self, text="Salvar", command=self.salvar_capacete).grid(row=4, column=0, columnspan=2, pady=10)
    
    def salvar_capacete(self):
        # Aqui você pode implementar a função de salvar o capacete no banco de dados,
        # similar à função inserir_empresa(), se necessário. Por enquanto, apenas exibe uma mensagem.
        messagebox.showinfo("Informação", "Capacete salvo (função a ser implementada).")
        self.master.master.show_main_menu()

# Novas telas para entidades adicionais

class ContratoFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Cadastro de Contrato", font=('Helvetica', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        ttk.Label(self, text="ID da Empresa:").grid(row=1, column=0, sticky="w")
        self.entry_id_empresa = ttk.Entry(self)
        self.entry_id_empresa.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Data do Contrato (AAAA-MM-DD):").grid(row=2, column=0, sticky="w")
        self.entry_data_contrato = ttk.Entry(self)
        self.entry_data_contrato.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Prazo (dias):").grid(row=3, column=0, sticky="w")
        self.entry_prazo = ttk.Entry(self)
        self.entry_prazo.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Valor do Serviço:").grid(row=4, column=0, sticky="w")
        self.entry_valor_servico = ttk.Entry(self)
        self.entry_valor_servico.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Data de Contato (AAAA-MM-DD):").grid(row=5, column=0, sticky="w")
        self.entry_data_contato = ttk.Entry(self)
        self.entry_data_contato.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(self, text="Salvar", command=self.salvar_contrato).grid(row=6, column=0, columnspan=2, pady=10)
    
    def salvar_contrato(self):
        try:
            id_empresa = int(self.entry_id_empresa.get())
            data_contrato = self.entry_data_contrato.get()
            prazo = int(self.entry_prazo.get())
            valor_servico = float(self.entry_valor_servico.get())
            data_contato = self.entry_data_contato.get()
        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores inseridos (ID, prazo e valor devem ser numéricos).")
            return
        inserir_contrato(id_empresa, data_contrato, prazo, valor_servico, data_contato)
        self.master.master.show_main_menu()

class RelatorioFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Gerar Relatório", font=('Helvetica', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        ttk.Label(self, text="ID do Ensaio:").grid(row=1, column=0, sticky="w")
        self.entry_id_ensaio = ttk.Entry(self)
        self.entry_id_ensaio.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Texto do Relatório:").grid(row=2, column=0, sticky="w")
        self.text_relatorio = tk.Text(self, height=10)
        self.text_relatorio.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(self, text="Salvar", command=self.salvar_relatorio).grid(row=3, column=0, columnspan=2, pady=10)
    
    def salvar_relatorio(self):
        try:
            ensaio_id = int(self.entry_id_ensaio.get())
        except ValueError:
            messagebox.showerror("Erro", "ID do Ensaio deve ser numérico.")
            return
        texto_relatorio = self.text_relatorio.get("1.0", tk.END).strip()
        if not texto_relatorio:
            messagebox.showerror("Erro", "O relatório não pode estar vazio.")
            return
        inserir_relatorio(ensaio_id, texto_relatorio)
        self.master.master.show_main_menu()

class SaidaDigitalFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Cadastro de Saída Digital", font=('Helvetica', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        ttk.Label(self, text="ID do Ensaio:").grid(row=1, column=0, sticky="w")
        self.entry_id_ensaio = ttk.Entry(self)
        self.entry_id_ensaio.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Canal:").grid(row=2, column=0, sticky="w")
        self.entry_canal = ttk.Entry(self)
        self.entry_canal.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Valor (0 ou 1):").grid(row=3, column=0, sticky="w")
        self.entry_valor = ttk.Entry(self)
        self.entry_valor.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self, text="Tempo de Ativação (s):").grid(row=4, column=0, sticky="w")
        self.entry_tempo = ttk.Entry(self)
        self.entry_tempo.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(self, text="Salvar", command=self.salvar_saida).grid(row=5, column=0, columnspan=2, pady=10)
    
    def salvar_saida(self):
        try:
            ensaio_id = int(self.entry_id_ensaio.get())
            canal = self.entry_canal.get()
            valor = bool(int(self.entry_valor.get()))
            tempo = float(self.entry_tempo.get())
        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores inseridos (ID e tempo numéricos; valor 0 ou 1).")
            return
        inserir_saidaDigital(ensaio_id, canal, valor, tempo)
        self.master.master.show_main_menu()


# ===========================#
# Classe Principal: MainApp
# ===========================#

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Software de Ensaio de Capacete")
        self.geometry("900x650")
        self.configure(bg="#f0f0f0")
        
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        self.style.configure("TButton", font=("Helvetica", 10))
        
        # Áreas de navegação e conteúdo
        self.nav_frame = ttk.Frame(self, width=220, padding=10)
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
            ("Empresa", lambda: self.load_content(EmpresaFrame)),
            ("Capacetes", lambda: self.load_content(CapacetesFrame)),
            ("Contrato", lambda: self.load_content(ContratoFrame)),
            ("Relatório", lambda: self.load_content(RelatorioFrame)),
            ("Saída Digital", lambda: self.load_content(SaidaDigitalFrame)),
            ("Sobre", lambda: self.load_content(AboutFrame))
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

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
