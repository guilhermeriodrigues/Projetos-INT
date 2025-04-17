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
    'password': 'sua_senha',
    'database': 'ensaios_capacetes',
    'auth_plugin': 'mysql_native_password'
}

# --- Funções de Inserção no BD (mantidas iguais) ---

def inserir_ensaio():
    try:
        conn = mysql.connector.connect(**db_config)
        cur  = conn.cursor()
        cur.execute("INSERT INTO Ensaio (id_contrato, id_capacete) VALUES (NULL,NULL)")
        conn.commit()
        eid = cur.lastrowid
        cur.close(); conn.close()
        return eid
    except Error as e:
        messagebox.showerror("Erro", f"Erro ao inserir ensaio: {e}")
        return None

def inserir_ensaio_impacto(ensaio_id, num_amostra, num_procedimento, posicao_teste, condicionamento, norma):
    try:
        conn = mysql.connector.connect(**db_config)
        cur  = conn.cursor()
        sql = """INSERT INTO EnsaioImpacto
                 (id_ensaio, num_amostra, num_procedimento, posicao_teste,
                  condicionamento, standard_utilizado, temperatura, umidade,
                  valor_atrito, norma, acel_x, acel_y, acel_z, tempo_amostra, notas)
                 VALUES (%s,%s,%s,%s,%s,%s,NULL,NULL,NULL,%s,NULL,NULL,NULL,NULL,NULL)"""
        cur.execute(sql, (ensaio_id, num_amostra, num_procedimento,
                          posicao_teste, condicionamento, norma, norma))
        conn.commit()
        cur.close(); conn.close()
        return True
    except Error as e:
        messagebox.showerror("Erro", f"Erro ao inserir ensaio de impacto: {e}")
        return False

def inserir_acelerometro(acel_x, acel_y, acel_z):
    try:
        conn = mysql.connector.connect(**db_config)
        cur  = conn.cursor()
        tempo = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = """UPDATE EnsaioImpacto
                 SET acel_x=%s, acel_y=%s, acel_z=%s, tempo_amostra=%s
                 WHERE id_ensaio=(SELECT MAX(id_ensaio) FROM Ensaio)"""
        cur.execute(sql, (acel_x, acel_y, acel_z, tempo))
        conn.commit()
        cur.close(); conn.close()
        messagebox.showinfo("Sucesso", "Acelerômetro salvo!")
    except Error as e:
        messagebox.showerror("Erro BD", f"{e}")

def inserir_empresa(nome, cidade, pais, estado, cnpj, tel, email):
    try:
        conn = mysql.connector.connect(**db_config)
        cur  = conn.cursor()
        sql = """INSERT INTO Empresa
                 (nome, cidade, pais, estado, cnpj, telefone, email)
                 VALUES (%s,%s,%s,%s,%s,%s,%s)"""
        cur.execute(sql, (nome,cidade,pais,estado,cnpj,tel,email))
        conn.commit()
        cur.close(); conn.close()
        messagebox.showinfo("Sucesso", "Empresa cadastrada!")
    except Error as e:
        messagebox.showerror("Erro BD", f"{e}")

def inserir_contrato(id_emp, data_ctr, prazo, valor, data_contato):
    try:
        conn = mysql.connector.connect(**db_config)
        cur  = conn.cursor()
        sql = """INSERT INTO Contrato
                 (id_empresa, data_contrato, prazo, valor_servico, data_contato)
                 VALUES (%s,%s,%s,%s,%s)"""
        cur.execute(sql, (id_emp,data_ctr,prazo,valor,data_contato))
        conn.commit()
        cur.close(); conn.close()
        messagebox.showinfo("Sucesso", "Contrato cadastrado!")
    except Error as e:
        messagebox.showerror("Erro BD", f"{e}")

def inserir_relatorio(ensaio_id, texto):
    try:
        conn = mysql.connector.connect(**db_config)
        cur  = conn.cursor()
        cur.execute("INSERT INTO Relatorio (id_ensaio,texto_relatorio) VALUES (%s,%s)",
                    (ensaio_id,texto))
        conn.commit()
        cur.close(); conn.close()
        messagebox.showinfo("Sucesso", "Relatório salvo!")
    except Error as e:
        messagebox.showerror("Erro BD", f"{e}")

def inserir_saidaDigital(ensaio_id, canal, valor, tempo):
    try:
        conn = mysql.connector.connect(**db_config)
        cur  = conn.cursor()
        cur.execute("INSERT INTO SaidaDigital (id_ensaio,canal,valor,tempo_ativacao) VALUES (%s,%s,%s,%s)",
                    (ensaio_id,canal,valor,tempo))
        conn.commit()
        cur.close(); conn.close()
        messagebox.showinfo("Sucesso", "Saída digital salva!")
    except Error as e:
        messagebox.showerror("Erro BD", f"{e}")

# --- Frames de Funcionalidade ---

class ElevatorAdjustment(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.grid(sticky="nsew", padx=10, pady=10)
        self.step = 1
        self.position = tk.IntVar(value=0)  # <— CORRETO
        ttk.Label(self, text="Ajuste Fino do Elevador", font=('Helvetica',12,'bold')).grid(row=0,column=0,columnspan=2)
        ttk.Label(self, text="Posição (mm):").grid(row=1,column=0,sticky="w")
        ttk.Label(self, textvariable=self.position).grid(row=1,column=1,sticky="w")
        ttk.Button(self, text="+1mm", command=lambda: self.position.set(self.position.get()+self.step)).grid(row=2,column=0)
        ttk.Button(self, text="-1mm", command=lambda: self.position.set(self.position.get()-self.step)).grid(row=2,column=1)

class FrictionSetting(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Configuração do Atrito", font=('Helvetica',12,'bold')).grid(row=0,column=0,columnspan=2)
        self.friction = tk.DoubleVar()
        ttk.Label(self, text="Valor do Atrito:").grid(row=1,column=0,sticky="w")
        ttk.Entry(self, textvariable=self.friction).grid(row=1,column=1,sticky="w")
        ttk.Button(self, text="Salvar", command=lambda: inserir_ensaio()).grid(row=2,column=0,columnspan=2)

class SensorCorrection(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Correção dos Acelerômetros", font=('Helvetica',12,'bold')).grid(row=0,column=0,columnspan=2)
        self.cx = tk.DoubleVar(); self.cy = tk.DoubleVar(); self.cz = tk.DoubleVar()
        for i, (lbl,var) in enumerate([("Canal X:",self.cx),("Canal Y:",self.cy),("Canal Z:",self.cz)],1):
            ttk.Label(self, text=lbl).grid(row=i,column=0,sticky="w")
            ttk.Entry(self, textvariable=var).grid(row=i,column=1,sticky="w")
        ttk.Button(self, text="Aplicar", command=lambda: None).grid(row=4,column=0,columnspan=2)

class TestSetup(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Configuração do Teste", font=('Helvetica',12,'bold')).grid(row=0,column=0,columnspan=2)
        ttk.Button(self, text="Plana", command=lambda: None).grid(row=1,column=0)
        ttk.Button(self, text="Hemi.", command=lambda: None).grid(row=1,column=1)

class TestRegistration(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Registro dos Dados", font=('Helvetica',12,'bold')).grid(row=0,column=0,columnspan=2)
        self.entries = {}
        fields = ["Número Amostra","Nº Procedimento","Posição","Condicionamento","Norma"]
        for i,f in enumerate(fields,1):
            ttk.Label(self, text=f+":").grid(row=i,column=0,sticky="w")
            e = ttk.Entry(self); e.grid(row=i,column=1,sticky="ew")
            self.entries[f] = e
        ttk.Button(self, text="Salvar", command=self._salvar).grid(row=len(fields)+1,column=0,columnspan=2)
    def _salvar(self):
        data = [e.get() for e in self.entries.values()]
        eid = inserir_ensaio()
        if eid: inserir_ensaio_impacto(eid,*data)

class SensorMonitor(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Monitor de Sensores", font=('Helvetica',12,'bold')).grid(row=0,column=0,columnspan=2)
        self.ax = ttk.Entry(self); self.ay = ttk.Entry(self); self.az = ttk.Entry(self)
        for i,(lbl,ent) in enumerate([("X mV/g:",self.ax),("Y mV/g:",self.ay),("Z mV/g:",self.az)],1):
            ttk.Label(self, text=lbl).grid(row=i,column=0,sticky="w")
            ent.grid(row=i,column=1,sticky="w")
        ttk.Button(self, text="Start", command=lambda: inserir_acelerometro(
            float(self.ax.get()),float(self.ay.get()),float(self.az.get()))).grid(row=4,column=0,columnspan=2)

class AboutFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Sobre", font=('Helvetica',14,'bold')).pack()
        ttk.Label(self, text="Ensaio de Capacete v1.0\n© 2025").pack()

class EmpresaFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Empresa", font=('Helvetica',14,'bold')).grid(row=0,column=0,columnspan=2)
        self.nm = ttk.Entry(self); self.ct = ttk.Entry(self); self.pais=ttk.Entry(self)
        self.est=ttk.Entry(self); self.cnpj=ttk.Entry(self); self.tel=ttk.Entry(self); self.email=ttk.Entry(self)
        labels = ["Nome","Cidade","País","Estado","CNPJ","Tel","Email"]
        ents   = [self.nm,self.ct,self.pais,self.est,self.cnpj,self.tel,self.email]
        for i,(l,e) in enumerate(zip(labels,ents),1):
            ttk.Label(self, text=l+":").grid(row=i,column=0,sticky="w")
            e.grid(row=i,column=1,sticky="ew")
        ttk.Button(self, text="Salvar", command=lambda: inserir_empresa(
            self.nm.get(),self.ct.get(),self.pais.get(),
            self.est.get(),self.cnpj.get(),self.tel.get(),self.email.get())
        ).grid(row=8,column=0,columnspan=2)

class CapacetesFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Capacete", font=('Helvetica',14,'bold')).grid(row=0,column=0,columnspan=2)
        self.mod = ttk.Entry(self); self.fab = ttk.Entry(self); self.tam=ttk.Entry(self)
        for i,(l,e) in enumerate(zip(["Modelo","Fabricante","Tamanho"],
                                     [self.mod,self.fab,self.tam]),1):
            ttk.Label(self, text=l+":").grid(row=i,column=0,sticky="w")
            e.grid(row=i,column=1,sticky="ew")
        ttk.Button(self, text="Salvar", command=lambda: messagebox.showinfo("OK","Implementar!")).grid(row=4,column=0,columnspan=2)

class ContratoFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Contrato", font=('Helvetica',14,'bold')).grid(row=0,column=0,columnspan=2)
        self.ide=ttk.Entry(self); self.dc=ttk.Entry(self); self.pr=ttk.Entry(self)
        self.vs=ttk.Entry(self); self.dcon=ttk.Entry(self)
        labels=["ID Empresa","Data (AAAA-MM-DD)","Prazo","Valor","Data Contato"]
        ents=[self.ide,self.dc,self.pr,self.vs,self.dcon]
        for i,(l,e) in enumerate(zip(labels,ents),1):
            ttk.Label(self, text=l+":").grid(row=i,column=0,sticky="w")
            e.grid(row=i,column=1,sticky="ew")
        ttk.Button(self, text="Salvar", command=lambda: inserir_contrato(
            int(self.ide.get()),self.dc.get(),int(self.pr.get()),
            float(self.vs.get()),self.dcon.get())
        ).grid(row=6,column=0,columnspan=2)

class RelatorioFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Relatório", font=('Helvetica',14,'bold')).grid(row=0,column=0,columnspan=2)
        self.id_e = ttk.Entry(self)
        self.txt  = tk.Text(self, height=8)
        ttk.Label(self, text="ID Ensaio:").grid(row=1,column=0,sticky="w")
        self.id_e.grid(row=1,column=1,sticky="ew")
        ttk.Label(self, text="Texto:").grid(row=2,column=0,sticky="nw")
        self.txt.grid(row=2,column=1,sticky="ew")
        ttk.Button(self, text="Salvar", command=lambda: inserir_relatorio(
            int(self.id_e.get()), self.txt.get("1.0","end").strip())
        ).grid(row=3,column=0,columnspan=2)

class SaidaDigitalFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Saída Digital", font=('Helvetica',14,'bold')).grid(row=0,column=0,columnspan=2)
        self.ide=ttk.Entry(self); self.can=ttk.Entry(self)
        self.val=ttk.Entry(self); self.tem=ttk.Entry(self)
        labels=["ID Ensaio","Canal","Valor(0/1)","Tempo(s)"]
        ents=[self.ide,self.can,self.val,self.tem]
        for i,(l,e) in enumerate(zip(labels,ents),1):
            ttk.Label(self, text=l+":").grid(row=i,column=0,sticky="w")
            e.grid(row=i,column=1,sticky="ew")
        ttk.Button(self, text="Salvar", command=lambda: inserir_saidaDigital(
            int(self.ide.get()), self.can.get(), bool(int(self.val.get())), float(self.tem.get()))
        ).grid(row=5,column=0,columnspan=2)

# --- MainApp com Notebook e Status Bar ---

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Software de Ensaio de Capacete")
        self.geometry("900x650")
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Notebook (abas no topo)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # registra todos os frames no notebook
        frames = [
            (ElevatorAdjustment,    "Ajuste Elevador"),
            (FrictionSetting,       "Atrito"),
            (SensorMonitor,         "Monitor Sensor"),
            (SensorCorrection,      "Correção ACC"),
            (TestRegistration,      "Registro Dados"),
            (TestSetup,             "Configurações"),
            (EmpresaFrame,          "Empresa"),
            (CapacetesFrame,        "Capacetes"),
            (ContratoFrame,         "Contrato"),
            (RelatorioFrame,        "Relatório"),
            (SaidaDigitalFrame,     "Saída Digital"),
            (AboutFrame,            "Sobre"),
        ]
        for cls, title in frames:
            frame = cls(self.notebook, self)
            self.notebook.add(frame, text=title)

        # Status bar
        self.status = ttk.Label(self, text="Pronto", relief="sunken", anchor="w")
        self.status.pack(fill="x", side="bottom")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
