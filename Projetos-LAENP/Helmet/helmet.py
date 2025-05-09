import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageSequence
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import serial 
import threading
import random
import time
import sys

if sys.platform.startswith("linux"):
    import smbus2
    RealSMBus = smbus2.SMBus
else:
    # FakeSMBus para Windows
    class FakeSMBus:
        def _init_(self, bus): pass
        def read_i2c_block_data(self, addr, reg, length):
            # gera 3 eixos aleatórios
            import random
            # simula raw: valores entre -2048 e +2047 (14‑bit >>2)
            def sim(): return random.randint(-2048,2047)
            # retorna como 6 bytes MSB/LSB
            def to_bytes(v):
                raw = (v & 0x3FFF) << 2
                return [(raw>>8)&0xFF, raw&0xFF]
            b = to_bytes(sim()) + to_bytes(sim()) + to_bytes(sim())
            return b

    RealSMBus = FakeSMBus


ARDUINO_PORT = "COM3"      
ARDUINO_BAUD = 9600
ser = None

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sua_senha',
    'database': 'ensaios_capacete',
    'auth_plugin': 'mysql_native_password'
}



def inserir_ensaio():
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        cur.execute("INSERT INTO Ensaio (id_contrato, id_capacete) VALUES (NULL, NULL)")
        cnx.commit()
        eid = cur.lastrowid
        cur.close(); cnx.close()
        return eid
    except Error as e:
        messagebox.showerror("Erro", f"Erro ao inserir ensaio: {e}")
        return None


def atualizar_ensaio(ensaio_id, id_contrato, id_capacete):
    """
    Atualiza o registro de Ensaio com os IDs de contrato e capacete selecionados.
    """
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        sql = "UPDATE Ensaio SET id_contrato=%s, id_capacete=%s WHERE id_ensaio=%s"
        cur.execute(sql, (id_contrato, id_capacete, ensaio_id))
        cnx.commit()
        cur.close()
        cnx.close()
    except Error as e:
        print(f"Erro ao atualizar o ensaio: {e}") 

        
def inserir_ensaio_impacto(ensaio_id, num_amostra, num_procedimento, posicao_teste, condicionamento, norma):
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        sql = """
          INSERT INTO EnsaioImpacto 
            (id_ensaio, num_amostra, num_procedimento, posicao_teste,
             condicionamento, standard_utilizado, temperatura, umidade,
             valor_atrito, norma, acel_x, acel_y, acel_z, tempo_amostra, notas)
          VALUES (%s,%s,%s,%s,%s,%s,NULL,NULL,NULL,%s,NULL,NULL,NULL,NULL,NULL)
        """
        cur.execute(sql, (ensaio_id, num_amostra, num_procedimento,
                          posicao_teste, condicionamento, norma, norma))
        cnx.commit()
        cur.close(); cnx.close()
        return True
    except Error as e:
        messagebox.showerror("Erro", f"Erro ao inserir ensaio de impacto: {e}")
        return False

def inserir_acelerometro(acel_x, acel_y, acel_z, ensaio_id):
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        tempo = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = """
          UPDATE EnsaioImpacto
            SET acel_x=%s, acel_y=%s, acel_z=%s, tempo_amostra=%s
          WHERE id_ensaio=%s
        """
        cur.execute(sql, (acel_x, acel_y, acel_z, tempo, ensaio_id))
        cnx.commit()
        cur.close(); cnx.close()
        messagebox.showinfo("Sucesso", "Acelerômetro salvo!")
    except Error as e:
        messagebox.showerror("Erro", f"Erro ao salvar acelerômetro: {e}")

def inserir_relatorio(ensaio_id, texto):
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        cur.execute("INSERT INTO Relatorio(id_ensaio,texto_relatorio) VALUES (%s,%s)",
                    (ensaio_id, texto))
        cnx.commit()
        cur.close(); cnx.close()
        messagebox.showinfo("Sucesso", "Relatório salvo!")
    except Error as e:
        messagebox.showerror("Erro", f"Erro ao salvar relatório: {e}")

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

def inserir_capacete(modelo, fabricante, tamanho):
    try:
        conn = mysql.connector.connect(**db_config)
        cur  = conn.cursor()
        sql = """INSERT INTO Capacete (modelo, fabricante, tamanho)
                 VALUES (%s,%s,%s)"""
        cur.execute(sql, (modelo, fabricante, tamanho))
        conn.commit()
        cur.close(); conn.close()
        messagebox.showinfo("Sucesso", "Capacete cadastrado!")
    except Error as e:
        messagebox.showerror("Erro BD", f"{e}")


class FakeRaspberry:
    """
    Simula um sensor acelerômetro rodando no Raspberry Pi.
    Gera leituras periódicas dos eixos X, Y, Z.
    """
    def _init_(self, interval=0.05):
        self.interval = interval
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.offset_z = 0.0
        self.running = False
        self._callbacks = []

    def start(self):
        """Inicia a thread que gera leituras fake."""
        if not self.running:
            self.running = True
            threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        """Para a geração de leituras."""
        self.running = False

    def _run(self):
        while self.running:
            # Gera valores pseudo‑randômicos para simular o sensor
            x = random.uniform(-2.0, 2.0) + self.offset_x
            y = random.uniform(-2.0, 2.0) + self.offset_y
            z = random.uniform(-2.0, 2.0) + self.offset_z
            # Notifica todos os inscritos
            for cb in self._callbacks:
                try:
                    cb(x, y, z)
                except:
                    pass
            time.sleep(self.interval)

    def register_callback(self, callback):
        """Registra uma função callback(x,y,z) para receber leituras."""
        self._callbacks.append(callback)

    def apply_offsets(self, ox, oy, oz):
        """Atualiza os offsets de calibração."""
        self.offset_x = ox
        self.offset_y = oy
        self.offset_z = oz


class ElevatorAdjustment(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller 
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
        self.controller = controller 
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Configuração do Atrito", font=('Helvetica',12,'bold')).grid(row=0,column=0,columnspan=2)
        self.friction = tk.DoubleVar()
        ttk.Label(self, text="Valor do Atrito:").grid(row=1,column=0,sticky="w")
        ttk.Entry(self, textvariable=self.friction).grid(row=1,column=1,sticky="w")
        ttk.Button(self, text="Salvar", command=lambda: inserir_ensaio()).grid(row=2,column=0,columnspan=2)

# variáveis globais de correção
offset_x = 0.0
offset_y = 0.0
offset_z = 0.0

class SensorCorrection(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Correção dos Acelerômetros", font=( 'Helvetica',12,'bold')).grid(row=0,column=0,columnspan=2)
        self.cx = tk.DoubleVar(); self.cy = tk.DoubleVar(); self.cz = tk.DoubleVar()
        for i,(lbl,var) in enumerate([("Canal X:",self.cx),("Canal Y:",self.cy),("Canal Z:",self.cz)],1):
            ttk.Label(self, text=lbl).grid(row=i,column=0,sticky="w")
            ttk.Entry(self, textvariable=var).grid(row=i,column=1,sticky="w")
        ttk.Button(self, text="Aplicar", command=self.apply).grid(row=4,column=0,columnspan=2)
    def apply(self):
        global offset_x, offset_y, offset_z
        offset_x,offset_y,offset_z = self.cx.get(), self.cy.get(), self.cz.get()
        messagebox.showinfo("Calibração", f"Offsets aplicados:\nX={offset_x}, Y={offset_y}, Z={offset_z}")

class TestSetup(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(sticky="nsew",padx=20,pady=20)
        ttk.Label(self,text="Configuração do Teste",font=('Helvetica',12,'bold'))\
            .grid(row=0,column=0,columnspan=2,pady=(0,10))
        ttk.Button(self,text="Plana",command=lambda: None).grid(row=1,column=0,padx=5,pady=5)
        ttk.Button(self,text="Hemisférica",command=lambda: None).grid(row=1,column=1,padx=5,pady=5)
        # botão "Voltar" encaminha para próximo passo no wizard
        self.btn = ttk.Button(self,text="Salvar",command=lambda: None)
        self.btn.grid(row=2,column=0,columnspan=2,pady=10)

class TestRegistration(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
    
        self.grid(sticky="nsew", padx=20, pady=20)
        ttk.Label(self, text="Registro dos Dados", font=('Helvetica',12,'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        # Combobox de Contrato
        ttk.Label(self, text="Contrato:").grid(row=1, column=0, sticky="w")
        self.combo_contrato = ttk.Combobox(self, state="readonly")
        self.combo_contrato.grid(row=1, column=1, sticky="ew", pady=2)
        self._load_contratos()
        # Combobox de Capacete
        ttk.Label(self, text="Capacete:").grid(row=2, column=0, sticky="w")
        self.combo_capacete = ttk.Combobox(self, state="readonly")
        self.combo_capacete.grid(row=2, column=1, sticky="ew", pady=2)
        self._load_capacetes()
        # Campos de impacto
        self.fields = ["Número da Amostra","Número do Procedimento/Relatório",
                       "Posição do Ensaio","Condicionamento","Norma Utilizada"]
        self.entries = {}
        for i, f in enumerate(self.fields, start=3):
            ttk.Label(self, text=f+":").grid(row=i, column=0, sticky="w", pady=2)
            e = ttk.Entry(self)
            e.grid(row=i, column=1, sticky="ew", pady=2)
            self.entries[f] = e
        # Botão "Salvar" será controlado pelo wizard
        self.btn = ttk.Button(self, text="Salvar", command=lambda: None)
        self.btn.grid(row=3+len(self.fields), column=0, columnspan=2, pady=10)

    def _load_contratos(self):
        try:
            cnx = mysql.connector.connect(**db_config)
            cur = cnx.cursor()
            cur.execute("SELECT id_contrato, id_empresa FROM Contrato")
            rows = cur.fetchall()
            cur.close(); cnx.close()
            self.combo_contrato['values'] = [f"{r[0]} (Emp {r[1]})" for r in rows]
        except Error as e:
            messagebox.showerror("Erro BD", f"{e}")

    def _load_capacetes(self):
        try:
            cnx = mysql.connector.connect(**db_config)
            cur = cnx.cursor()
            cur.execute("SELECT id_capacete, modelo FROM Capacete")
            rows = cur.fetchall()
            cur.close(); cnx.close()
            self.combo_capacete['values'] = [f"{r[0]} - {r[1]}" for r in rows]
        except Error as e:
            messagebox.showerror("Erro BD", f"{e}")

class SensorMonitor(ttk.Frame):
    def _init_(self, master, controller):
        super()._init_(master)
        self.controller = controller
        self.grid(sticky="nsew", padx=20, pady=20)

        # Fonte de dados
        ttk.Label(self, text="Fonte de Dados:").grid(row=0, column=0, sticky="w")
        self.src = ttk.Combobox(self, values=["Arduino","Raspberry Pi","Fake Raspberry"], state="readonly")
        self.src.current(0)
        self.src.grid(row=0, column=1, sticky="ew")

        # Leitura X/Y/Z
        self.eX = ttk.Entry(self, width=10); self.eY = ttk.Entry(self, width=10); self.eZ = ttk.Entry(self, width=10)
        for i, (lbl, ent) in enumerate([("X (m/s²):",self.eX),("Y (m/s²):",self.eY),("Z (m/s²):",self.eZ)], start=1):
            ttk.Label(self, text=lbl).grid(row=i, column=0, sticky="w")
            ent.grid(row=i, column=1, sticky="w")

        self.btn = ttk.Button(self, text="Salvar", command=self.save_reading)
        self.btn.grid(row=4, column=0, columnspan=2, pady=10)

        # I2C bus para Raspberry real
        self.i2c_bus = RealSMBus(1)

        # Fake Raspberry
        self.fake = FakeRaspberry()
        # registra callback para atualizar GUI a partir do fake
        self.fake.register_callback(self._update_fields)

        # start leitura contínua
        self.running = True
        threading.Thread(target=self._read_loop, daemon=True).start()

    def _read_loop(self):
        global ser, offset_x, offset_y, offset_z
        while self.running:
            src = self.src.get()

            if src == "Arduino":
                if ser and ser.in_waiting:
                    line = ser.readline().decode('ascii',errors='ignore').strip()
                    parts = line.split(',')
                    if len(parts)==3:
                        try:
                            x,y,z = [float(p) for p in parts]
                        except:
                            continue
                    else:
                        continue
                    # aplicar offsets
                    x -= offset_x; y -= offset_y; z -= offset_z
                    self._update_fields(x,y,z)

            elif src == "Raspberry Pi":
                try:
                    data = self.i2c_bus.read_i2c_block_data(0x1C, 0x00, 6)
                    x = (((data[0]<<8)|data[1]) >> 2) - offset_x
                    y = (((data[2]<<8)|data[3]) >> 2) - offset_y
                    z = (((data[4]<<8)|data[5]) >> 2) - offset_z
                    self._update_fields(x,y,z)
                except:
                    pass

            else:  # Fake Raspberry
                # garanta que a thread fake está rodando
                if not self.fake.running:
                    self.fake.start()

            time.sleep(0.05)

    def _update_fields(self, x, y, z):
        # é chamado tanto pelo loop serial quanto pelo fake callback
        self.eX.after(0, lambda v=x: self.eX.delete(0,'end') or self.eX.insert(0,f"{v:.3f}"))
        self.eY.after(0, lambda v=y: self.eY.delete(0,'end') or self.eY.insert(0,f"{v:.3f}"))
        self.eZ.after(0, lambda v=z: self.eZ.delete(0,'end') or self.eZ.insert(0,f"{v:.3f}"))

    def save_reading(self):
        try:
            x,y,z = float(self.eX.get()), float(self.eY.get()), float(self.eZ.get())
        except ValueError:
            messagebox.showerror("Erro","Leitura inválida")
            return
        inserir_acelerometro(x, y, z, self.controller.ensaio_id)
        messagebox.showinfo("Salvo","Leitura salva no banco.")

        
class AboutFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller 
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Sobre", font=('Helvetica',14,'bold')).pack()
        ttk.Label(self, text="Ensaio de Capacete v1.0\n© 2025").pack()

class EmpresaFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller 
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
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller 
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Capacete", font=('Helvetica',14,'bold')).grid(row=0,column=0,columnspan=2)
        self.mod = ttk.Entry(self); self.fab = ttk.Entry(self); self.tam=ttk.Entry(self)
        for i,(l,e) in enumerate(zip(["Modelo","Fabricante","Tamanho"],
                                     [self.mod,self.fab,self.tam]),1):
            ttk.Label(self, text=l+":").grid(row=i,column=0,sticky="w")
            e.grid(row=i,column=1,sticky="ew")
        ttk.Button(self, text="Salvar", command=self.salvar).grid(row=4,column=0,columnspan=2)

    def salvar(self):
        m,f,t = self.mod.get(), self.fab.get(), self.tam.get()
        if not (m and f and t):
            messagebox.showerror("Erro","Preencha todos os campos")
            return
        inserir_capacete(m,f,t)
        # limpa campos
        self.mod.delete(0,'end'); self.fab.delete(0,'end'); self.tam.delete(0,'end')

class ContratoFrame(ttk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller 
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Contrato", font=('Helvetica',14,'bold')).grid(row=0,column=0,columnspan=2)
        ttk.Label(self, text="Empresa:").grid(row=1,column=0,sticky="w")
        self.combo_emp = ttk.Combobox(self, state="readonly")
        self.combo_emp.grid(row=1,column=1,sticky="ew")
        self._carregar_empresas()
        ttk.Label(self, text="Data (YYYY-MM-DD):").grid(row=2,column=0,sticky="w")
        self.dc=ttk.Entry(self); self.dc.grid(row=2,column=1,sticky="ew")
        ttk.Label(self, text="Prazo (dias):").grid(row=3,column=0,sticky="w")
        self.pr=ttk.Entry(self); self.pr.grid(row=3,column=1,sticky="ew")
        ttk.Label(self, text="Valor:").grid(row=4,column=0,sticky="w")
        self.vs=ttk.Entry(self); self.vs.grid(row=4,column=1,sticky="ew")
        ttk.Label(self, text="Data Contato:").grid(row=5,column=0,sticky="w")
        self.dcon=ttk.Entry(self); self.dcon.grid(row=5,column=1,sticky="ew")
        ttk.Button(self, text="Salvar", command=self.salvar).grid(row=6,column=0,columnspan=2)

    def _carregar_empresas(self):
        try:
            cnx = mysql.connector.connect(**db_config)
            cur = cnx.cursor()
            cur.execute("SELECT id_empresa, nome FROM Empresa")
            rows = cur.fetchall()
            cur.close(); cnx.close()
            self.combo_emp['values'] = [f"{r[0]} - {r[1]}" for r in rows]
        except Error as e:
            messagebox.showerror("Erro BD", f"{e}")

    def salvar(self):
        sel = self.combo_emp.get()
        if not sel:
            messagebox.showerror("Erro","Selecione uma empresa")
            return
        id_emp = int(sel.split(" - ")[0])
        try:
            inserir_contrato(id_emp,
                             self.dc.get(),
                             int(self.pr.get()),
                             float(self.vs.get()),
                             self.dcon.get())
        except ValueError:
            messagebox.showerror("Erro","Valores numéricos inválidos")


class RelatorioFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(sticky="nsew",padx=20,pady=20)
        ttk.Label(self,text="Gerar Relatório",font=('Helvetica',12,'bold'))\
            .grid(row=0,column=0,columnspan=2,pady=(0,10))
        ttk.Label(self,text="ID Ensaio:").grid(row=1,column=0,sticky="w")
        self.eID = ttk.Entry(self); self.eID.grid(row=1,column=1,sticky="ew")
        ttk.Label(self,text="Texto:").grid(row=2,column=0,sticky="nw")
        self.txt = tk.Text(self,height=8); self.txt.grid(row=2,column=1,sticky="ew")
        self.btn = ttk.Button(self,text="Salvar",command=lambda: None)
        self.btn.grid(row=3,column=0,columnspan=2,pady=10)

class SaidaDigitalFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller 
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



class NovoEnsaioWizard(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Fluxo: Novo Ensaio")
        self.geometry("600x400")
        self.master = master  # referência ao MainApp
        # criar um container para trocar de frame
        self.container = ttk.Frame(self)
        self.container.pack(expand=True, fill="both")
        # iniciar ensaio no banco
        self.ensaio_id = inserir_ensaio()
        # definir sequência de classes
        self.steps = [TestRegistration, TestSetup, SensorMonitor, RelatorioFrame]
        self.index = 0
        self.show_step()

    def show_step(self):
    
        for w in self.container.winfo_children(): w.destroy()
        cls = self.steps[self.index]
        # instancia com ou sem controller
        if cls is SensorMonitor:
            frame = cls(self.container, self)
        else:
            frame = cls(self.container)
        # configura botão
        if isinstance(frame, TestRegistration): frame.btn.config(text="Próximo", command=self.save_registration)
        elif isinstance(frame, TestSetup): frame.btn.config(text="Próximo", command=self.save_setup)
        elif isinstance(frame, SensorMonitor): frame.btn.config(text="Próximo", command=self.save_sensor)
        elif isinstance(frame, RelatorioFrame): frame.btn.config(text="Finalizar", command=self.save_report)
            
            
            
        
    def save_registration(self):
        frm = self.container.winfo_children()[0]
        # validação: nenhum campo pode ficar vazio
        for field, entry in frm.entries.items():
            if not entry.get().strip():
                messagebox.showerror("Erro", f"O campo “{field}” é obrigatório.")
                return
        # se chegou aqui, todos preenchidos:
        vals = {f: frm.entries[f].get().strip() for f in frm.fields}
        inserir_ensaio_impacto(
            self.ensaio_id,
            vals["Número da Amostra"],
            vals["Número do Procedimento/Relatório"],
            vals["Posição do Ensaio"],
            vals["Condicionamento"],
            vals["Norma Utilizada"]
        )
        self.index += 1
        self.show_step()

    def save_setup(self):
        # (se houver algum dado a salvar aqui, faria aqui)
        self.index += 1
        self.show_step()

    def save_sensor(self):
        frm = self.container.winfo_children()[0]
        try:
            x = float(frm.eX.get()); y = float(frm.eY.get()); z = float(frm.eZ.get())
        except ValueError:
            messagebox.showerror("Erro","Insira valores numéricos válidos")
            return
        inserir_acelerometro(x,y,z,self.ensaio_id)
        self.index += 1
        self.show_step()

    def save_report(self):
        frm = self.container.winfo_children()[0]
        try:
            idx = int(frm.eID.get())
        except ValueError:
            messagebox.showerror("Erro","ID Inválido")
            return
        texto = frm.txt.get("1.0","end").strip()
        if not texto:
            messagebox.showerror("Erro","Relatório vazio")
            return
        inserir_relatorio(idx, texto)
        messagebox.showinfo("Concluído","Ensaio finalizado com sucesso!")
        self.destroy()




class EnsaiosConcluidosFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller 
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Ensaios Concluídos", font=('Helvetica',14,'bold')).pack(anchor="w")
   
        cols = ("ID","Amostra","Proced.","Empresa","Capacete","Data")
        self.tv = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tv.heading(c,text=c)
            self.tv.column(c,width=100)
        self.tv.pack(expand=True, fill="both")
        self.tv.bind("<<TreeviewSelect>>", self.on_select)
       
        self.txt = tk.Text(self, height=8)
        self.txt.pack(expand=True, fill="x", pady=10)
        self.carregar_ensaio()

    def carregar_ensaio(self):
        # busca apenas ensaios com relatório
        try:
            cnx = mysql.connector.connect(**db_config)
            cur = cnx.cursor()
            sql = """
              SELECT e.id_ensaio, ei.num_amostra, ei.num_procedimento,
                     emp.nome, cap.modelo, e.data_ensaio
              FROM Ensaio e
                JOIN EnsaioImpacto ei ON e.id_ensaio=ei.id_ensaio
                LEFT JOIN Relatorio r ON e.id_ensaio=r.id_ensaio
                LEFT JOIN Empresa emp ON e.id_contrato=(
                    SELECT id_contrato FROM Contrato WHERE id_contrato=e.id_contrato
                )
                LEFT JOIN Capacete cap ON e.id_capacete=cap.id_capacete
              WHERE r.id_relatorio IS NOT NULL
              ORDER BY e.data_ensaio DESC
            """
            cur.execute(sql)
            for row in cur.fetchall():
                self.tv.insert("","end",values=row)
            cur.close(); cnx.close()
        except Error as e:
            messagebox.showerror("Erro BD", str(e))

    def on_select(self, evt):
        sel = self.tv.selection()
        if not sel: return
        ens_id = self.tv.item(sel[0])["values"][0]
        # carregar todos os detalhes
        try:
            cnx = mysql.connector.connect(**db_config)
            cur = cnx.cursor()
            sql = """
              SELECT emp.nome, ctr.prazo, cap.modelo, ei.*, r.texto_relatorio
              FROM Ensaio e
                JOIN EnsaioImpacto ei ON e.id_ensaio=ei.id_ensaio
                LEFT JOIN Relatorio r ON e.id_ensaio=r.id_ensaio
                LEFT JOIN Contrato ctr ON e.id_contrato=ctr.id_contrato
                LEFT JOIN Empresa emp ON ctr.id_empresa=emp.id_empresa
                LEFT JOIN Capacete cap ON e.id_capacete=cap.id_capacete
              WHERE e.id_ensaio=%s
            """
            cur.execute(sql,(ens_id,))
            rec=cur.fetchone()
            cur.close(); cnx.close()
            # exibe
            self.txt.delete("1.0","end")
            labels = ["Empresa","Prazo(dias)","Capacete",
                      "ID Impacto","Amostra","Proced.","Posição","Cond.","Std",
                      "Temp","Umid","Atrito","Norma","aX","aY","aZ","tAm","Notas","Relatório"]
            for lab,val in zip(labels,rec):
                self.txt.insert("end",f"{lab}: {val}\n")
        except Error as e:
            messagebox.showerror("Erro BD", str(e))


# --- MainApp com Notebook e Status Bar ---

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        start_serial()
        self.title("Software de Ensaio de Capacete")
        self.geometry("900x650")
        self.configure(bg="#f0f0f0")
        self.style = ttk.Style(self); self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica",10))
        self.style.configure("TButton", font=("Helvetica",10))

        self.nav = ttk.Frame(self, width=200, padding=10)
        self.nav.grid(row=0,column=0,sticky="ns")
        self.content = ttk.Frame(self, padding=10)
        self.content.grid(row=0,column=1,sticky="nsew")
        self.columnconfigure(1, weight=1); self.rowconfigure(0, weight=1)

        ttk.Button(self.nav, text="▶ Novo Ensaio", command=lambda: NovoEnsaioWizard(self))\
            .grid(row=0,column=0,pady=5,sticky="ew")

        nav_items = [
            ("Ensaios Concluídos", lambda: self.load(EnsaiosConcluidosFrame)),
            ("Empresa", lambda: self.load(EmpresaFrame)),
            ("Capacetes", lambda: self.load(CapacetesFrame)),
            ("Contrato", lambda: self.load(ContratoFrame)),
            ("Saída Digital", lambda: self.load(SaidaDigitalFrame)),
            ("Sobre", lambda: self.load(AboutFrame)),
        ]
        for i,(txt,cmd) in enumerate(nav_items, start=1):
            ttk.Button(self.nav, text=txt, command=cmd).grid(row=i,column=0,pady=5,sticky="ew")

        self.show_welcome()

    def show_welcome(self):
        for w in self.content.winfo_children(): w.destroy()
        ttk.Label(self.content, text="Bem-vindo ao Software de Ensaio de Capacetes",
                  font=("Helvetica",14)).pack(expand=True)

    def load(self, cls):
        for w in self.content.winfo_children(): w.destroy()
        frame = cls(self.content, self)
        frame.grid(sticky="nsew")

if __name__ == "__main__":
    
    def start_serial():
     global ser
    try:
        ser = serial.Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=1)
    except Exception as e:
        print("Não foi possível abrir Serial:", e)

    threading.Thread(target=start_serial, daemon=True).start()
    
    
    app = MainApp()
    app.mainloop()
