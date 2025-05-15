import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageSequence
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import threading
import random
import time
import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib, os
from email.message import EmailMessage
from tkinter import simpledialog


try:
    import serial
except ImportError:
    serial = None

# Fake SMBus para Windows ou real para Linux
if sys.platform.startswith("linux"):
    import smbus2
    RealSMBus = smbus2.SMBus
else:
    class FakeSMBus:
        def __init__(self, bus): pass
        def read_i2c_block_data(self, addr, reg, length):
            # gera seis bytes simulados (14 bits >> 2)
            def sim(): return random.randint(-2048, 2047)
            def to_bytes(v): raw = (v & 0x3FFF) << 2; return [(raw >> 8) & 0xFF, raw & 0xFF]
            b = to_bytes(sim()) + to_bytes(sim()) + to_bytes(sim())
            return b
    RealSMBus = FakeSMBus

ARDUINO_PORT = None
ARDUINO_BAUD = None
ser = None

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sua_senha',
    'database': 'ensaios_capacete',
    'auth_plugin': 'mysql_native_password'
}

def start_serial():
    global ser
    if serial is None:
        print("pySerial não disponível; pulando Arduino")
        ser = None
        return
    try:
        ser = serial.Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=1)
        print(f"Serial aberta: {ARDUINO_PORT}@{ARDUINO_BAUD}")
    except Exception as e:
        ser = None
        print("Não foi possível abrir serial:", e)



def carregar_configuracoes():
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor(dictionary=True)
        cur.execute("SELECT * FROM Configuracoes ORDER BY id_config LIMIT 1")
        cfg = cur.fetchone()
        cur.close(); cnx.close()
        return cfg or {}
    except Error as e:
        messagebox.showerror("Erro BD", f"Não foi possível carregar configurações:\n{e}")
        return {}

def salvar_configuracoes(com_port, baud_rate, i2c_addr, ox, oy, oz):
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        # atualiza a única linha existente
        sql = """
          UPDATE Configuracoes
             SET com_port=%s, baud_rate=%s, i2c_addr=%s,
                 offset_x=%s, offset_y=%s, offset_z=%s
           WHERE id_config = (SELECT id_config FROM Configuracoes LIMIT 1)
        """
        cur.execute(sql, (com_port, baud_rate, i2c_addr, ox, oy, oz))
        cnx.commit()
        cur.close(); cnx.close()
        messagebox.showinfo("Configurações", "Preferências salvas com sucesso.")
    except Error as e:
        messagebox.showerror("Erro BD", f"Não foi possível salvar configurações:\n{e}")



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
        messagebox.showerror("Erro BD", f"Falha ao inserir Ensaio: {e}")
        return None

def atualizar_ensaio(ensaio_id, id_contrato, id_capacete):
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        cur.execute(
            "UPDATE Ensaio SET id_contrato=%s, id_capacete=%s WHERE id_ensaio=%s",
            (id_contrato, id_capacete, ensaio_id)
        )
        cnx.commit()
        cur.close(); cnx.close()
    except Error as e:
        messagebox.showerror("Erro BD", f"Falha ao atualizar Ensaio: {e}")

def inserir_ensaio_impacto(ensaio_id, num_amostra, num_procedimento,
                            posicao_teste, condicionamento, norma):
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        sql = (
            "INSERT INTO EnsaioImpacto (id_ensaio, num_amostra, num_procedimento,"
            " posicao_teste, condicionamento, standard_utilizado, temperatura, umidade,"
            " valor_atrito, norma, acel_x, acel_y, acel_z, tempo_amostra, notas)"
            " VALUES (%s,%s,%s,%s,%s,%s,NULL,NULL,NULL,%s,NULL,NULL,NULL,NULL,NULL)"
        )
        cur.execute(sql, (ensaio_id, num_amostra, num_procedimento,
                          posicao_teste, condicionamento, norma, norma))
        cnx.commit()
        cur.close(); cnx.close()
        return True
    except Error as e:
        messagebox.showerror("Erro BD", f"Falha ao inserir Impacto: {e}")
        return False

def inserir_acelerometro(acel_x, acel_y, acel_z, ensaio_id):
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        tempo = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(
            "UPDATE EnsaioImpacto SET acel_x=%s, acel_y=%s, acel_z=%s, tempo_amostra=%s"
            " WHERE id_ensaio=%s",
            (acel_x, acel_y, acel_z, tempo, ensaio_id)
        )
        cnx.commit()
        cur.close(); cnx.close()
    except Error as e:
        messagebox.showerror("Erro BD", f"Falha ao salvar acelerômetro: {e}")

def inserir_relatorio(ensaio_id, texto):
    if not texto.strip():
        messagebox.showerror("Erro", "Texto do relatório não pode ficar vazio.")
        return
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        cur.execute(
            "INSERT INTO Relatorio(id_ensaio, texto_relatorio) VALUES (%s,%s)",
            (ensaio_id, texto)
        )
        cnx.commit()
        cur.close(); cnx.close()
    except Error as e:
        messagebox.showerror("Erro BD", f"Falha ao inserir Relatório: {e}")

def inserir_empresa(nome, cidade, pais, estado, cnpj, tel, email):
    if not all([nome.strip(), cidade.strip(), pais.strip(), estado.strip(), cnpj.strip()]):
        messagebox.showerror("Erro", "Preencha todos os campos obrigatórios de Empresa.")
        return
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        cur.execute(
            "INSERT INTO Empresa(nome,cidade,pais,estado,cnpj,telefone,email)"
            " VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (nome, cidade, pais, estado, cnpj, tel, email)
        )
        cnx.commit()
        cur.close(); cnx.close()
    except Error as e:
        messagebox.showerror("Erro BD", f"Falha ao inserir Empresa: {e}")

def inserir_contrato(id_emp, data_ctr, prazo, valor, data_contato):
    if id_emp is None:
        messagebox.showerror("Erro", "Selecione uma empresa válida.")
        return
    try:
        prazo = int(prazo)
        valor = float(valor)
    except ValueError:
        messagebox.showerror("Erro", "Prazo e Valor devem ser numéricos.")
        return
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        cur.execute(
            "INSERT INTO Contrato(id_empresa,data_contrato,prazo,valor_servico,data_contato)"
            " VALUES (%s,%s,%s,%s,%s)",
            (id_emp, data_ctr, prazo, valor, data_contato)
        )
        cnx.commit()
        cur.close(); cnx.close()
    except Error as e:
        messagebox.showerror("Erro BD", f"Falha ao inserir Contrato: {e}")

def inserir_saidaDigital(ensaio_id, canal, valor, tempo):
    try:
        valor = int(valor)
        tempo = float(tempo)
    except ValueError:
        messagebox.showerror("Erro", "Valor e Tempo devem ser numéricos.")
        return
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        cur.execute(
            "INSERT INTO SaidaDigital(id_ensaio,canal,valor,tempo_ativacao) VALUES (%s,%s,%s,%s)",
            (ensaio_id, canal, valor, tempo)
        )
        cnx.commit()
        cur.close(); cnx.close()
    except Error as e:
        messagebox.showerror("Erro BD", f"Falha ao inserir Saída Digital: {e}")

def inserir_capacete(modelo, fabricante, tamanho):
    if not all([modelo.strip(), fabricante.strip(), tamanho.strip()]):
        messagebox.showerror("Erro", "Preencha todos os campos de Capacete.")
        return
    try:
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        cur.execute(
            "INSERT INTO Capacete(modelo,fabricante,tamanho) VALUES (%s,%s,%s)",
            (modelo, fabricante, tamanho)
        )
        cnx.commit()
        cur.close(); cnx.close()
    except Error as e:
        messagebox.showerror("Erro BD", f"Falha ao inserir Capacete: {e}")


offset_x = offset_y = offset_z = 0.0

def init_fake_raspberry():
    class FakeRaspberry:
        def __init__(self, interval=0.05):
            self.interval = interval
            self.offset_x = 0.0; self.offset_y = 0.0; self.offset_z = 0.0
            self.running = False; self._cbs = []
        def start(self):
            if not self.running:
                self.running = True
                threading.Thread(target=self._run, daemon=True).start()
        def stop(self): self.running = False
        def register_callback(self, cb): self._cbs.append(cb)
        def apply_offsets(self, ox, oy, oz):
            self.offset_x, self.offset_y, self.offset_z = ox, oy, oz
        def _run(self):
            while self.running:
                x = random.uniform(-2,2) + self.offset_x
                y = random.uniform(-2,2) + self.offset_y
                z = random.uniform(-2,2) + self.offset_z
                for cb in self._cbs:
                    try: cb(x,y,z)
                    except: pass
                time.sleep(self.interval)
    return FakeRaspberry

FakeRaspberry = init_fake_raspberry()


def gerar_pdf(texto_relatorio, ensaio_id, offset_x, offset_y, offset_z, leituras, pasta_rede):
    """
    texto_relatorio: str já salvo
    leituras: lista de (x,y,z, timestamp) — se quiser incluir
    pasta_rede: caminho onde salvar
    retorna path do PDF gerado
    """
    os.makedirs(pasta_rede, exist_ok=True)
    filename = f"Relatorio_Ensaio_{ensaio_id}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    path = os.path.join(pasta_rede, filename)

    c = canvas.Canvas(path, pagesize=A4)
    w,h = A4
    y = h - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Ensaio ID {ensaio_id} — Relatório")
    y -= 30

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Gerado em: {datetime.now():%Y-%m-%d %H:%M:%S}")
    y -= 20

    c.drawString(50, y, f"Offsets aplicados: X={offset_x:.3f}, Y={offset_y:.3f}, Z={offset_z:.3f}")
    y -= 30

    # (Opcional) incluir uma tabela simples de leituras
    if leituras:
        c.drawString(50, y, "Leituras (horário — X | Y | Z):")
        y -= 20
        for x,yv,zv,ts in leituras:
            line = f"{ts:%H:%M:%S}  {x:6.3f}  {yv:6.3f}  {zv:6.3f}"
            c.drawString(60, y, line)
            y -= 15
            if y < 100:
                c.showPage()
                y = h - 50
        y -= 20

    c.drawString(50, y, "Texto do Relatório:")
    y -= 20
    for linha in texto_relatorio.split("\n"):
        c.drawString(60, y, linha)
        y -= 15
        if y < 100:
            c.showPage()
            y = h - 50

    c.save()
    return path

    
def enviar_email_com_anexo(dest, assunto, corpo, caminho_pdf, smtp_cfg):
    """
    smtp_cfg: dict com keys smtp_server, smtp_port, smtp_user, smtp_pass
    """
    msg = EmailMessage()
    msg["From"]    = smtp_cfg["smtp_user"]
    msg["To"]      = dest
    msg["Subject"] = assunto
    msg.set_content(corpo)

    with open(caminho_pdf, "rb") as f:
        data = f.read()
        msg.add_attachment(data, maintype="application", subtype="pdf",
                           filename=os.path.basename(caminho_pdf))

    with smtplib.SMTP_SSL(smtp_cfg["smtp_server"], smtp_cfg["smtp_port"]) as s:
        s.login(smtp_cfg["smtp_user"], smtp_cfg["smtp_pass"])
        s.send_message(msg)



class ConfiguracoesFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid(sticky="nsew", padx=10, pady=10)
        ttk.Label(self, text="Configurações", font=('Helvetica',14,'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        
        # Carrega valores atuais
        cfg = carregar_configuracoes()
        
        # Campos
        labels = [
            ("Porta COM:",        cfg.get('com_port','COM3')),
            ("Baud rate:",        cfg.get('baud_rate',9600)),
            ("Endereço I²C:",     cfg.get('i2c_addr','0x1C')),
            ("Offset X (g):",     cfg.get('offset_x',0)),
            ("Offset Y (g):",     cfg.get('offset_y',0)),
            ("Offset Z (g):",     cfg.get('offset_z',0)),
        ]
        self.entries = {}
        for i,(lbl, val) in enumerate(labels, start=1):
            ttk.Label(self, text=lbl).grid(row=i, column=0, sticky="w", pady=2)
            e = ttk.Entry(self)
            e.insert(0, str(val))
            e.grid(row=i, column=1, sticky="ew", pady=2)
            self.entries[lbl] = e
        
        ttk.Button(self, text="Salvar", command=self._on_save)\
            .grid(row=len(labels)+1, column=0, columnspan=2, pady=10)

    def _on_save(self):
        try:
            com   = self.entries["Porta COM:"].get().strip()
            baud  = int(self.entries["Baud rate:"].get())
            i2c   = self.entries["Endereço I²C:"].get().strip()
            ox    = float(self.entries["Offset X (g):"].get())
            oy    = float(self.entries["Offset Y (g):"].get())
            oz    = float(self.entries["Offset Z (g):"].get())
        except ValueError:
            messagebox.showerror("Erro", "Verifique se todos os valores numéricos estão corretos.")
            return

        # Grava no banco
        salvar_configuracoes(com, baud, i2c, ox, oy, oz)
        # Atualiza variables globais / serial
        global ARDUINO_PORT, ARDUINO_BAUD, offset_x, offset_y, offset_z
        ARDUINO_PORT, ARDUINO_BAUD = com, baud
        offset_x, offset_y, offset_z = ox, oy, oz
        # Reinicia serial
        start_serial()


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
                       "Posição do Ensaio","Condicionamento"]
        self.entries = {}
        for i, f in enumerate(self.fields, start=3):
            ttk.Label(self, text=f+":").grid(row=i, column=0, sticky="w", pady=2)
            e = ttk.Entry(self)
            e.grid(row=i, column=1, sticky="ew", pady=2)
            self.entries[f] = e

        # Combobox de Norma
        ttk.Label(self, text="Norma Utilizada:").grid(row=3 + len(self.fields), column=0, sticky="w", pady=2)
        self.combo_norma = ttk.Combobox(
            self,
            state="readonly",
            values=[
                "ABNT NBR 7471:2015",
                "ECE 22.06",
                "ISO 565:1990",
                "ISO 6487"
            ]
        )
        self.combo_norma.grid(row=3 + len(self.fields), column=1, sticky="ew", pady=2)

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
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.grid(sticky="nsew", padx=20, pady=20)

        ttk.Label(self, text="Gerar Relatório", font=('Helvetica',12,'bold'))\
            .grid(row=0, column=0, columnspan=3, pady=(0,10))

        ttk.Label(self, text="ID Ensaio:").grid(row=1, column=0, sticky="w")
        self.eID = ttk.Entry(self); self.eID.grid(row=1, column=1, sticky="ew")

        ttk.Label(self, text="Texto:").grid(row=2, column=0, sticky="nw")
        self.txt = tk.Text(self, height=8); self.txt.grid(row=2, column=1, columnspan=2, sticky="ew")

        # Botões: Salvar / PDF / E-mail
        self.btn_salvar = ttk.Button(self, text="Salvar Texto", command=self._salvar_texto)
        self.btn_salvar.grid(row=3, column=0, pady=10)

        self.btn_pdf = ttk.Button(self, text="Gerar PDF", command=self._on_pdf)
        self.btn_pdf.grid(row=3, column=1, pady=10)

        self.btn_email = ttk.Button(self, text="Enviar por E-mail", command=self._on_email)
        self.btn_email.grid(row=3, column=2, pady=10)

    def _salvar_texto(self):
        try:
            idx   = int(self.eID.get())
            texto = self.txt.get("1.0", "end").strip()
            if not texto:
                raise ValueError("Texto vazio")
            inserir_relatorio(idx, texto)
            messagebox.showinfo("Sucesso", "Relatório salvo no BD.")
        except ValueError as e:
            messagebox.showerror("Erro", f"ID ou texto inválido: {e}")

    def _coletar_dados(self):
        """Busca leituras e offsets do ensaio no BD."""
        idx = int(self.eID.get())
        # leituras
        leituras = []
        cnx = mysql.connector.connect(**db_config)
        cur = cnx.cursor()
        cur.execute("SELECT acel_x, acel_y, acel_z, tempo_amostra FROM EnsaioImpacto WHERE id_ensaio=%s", (idx,))
        for x,y,z,ts in cur.fetchall():
            leituras.append((x,y,z, ts))
        # offsets globais
        from __main__ import offset_x, offset_y, offset_z
        # texto
        cur.execute("SELECT texto_relatorio FROM Relatorio WHERE id_ensaio=%s", (idx,))
        texto = cur.fetchone()[0]
        cur.close(); cnx.close()
        return idx, texto, leituras, (offset_x, offset_y, offset_z)

    def _on_pdf(self):
        try:
            ens_id, texto, leituras, offsets = self._coletar_dados()
            # pasta de rede fixa ou carregada de Configurações
            pasta = r"\\servidor\relatorios"
            pdf = gerar_pdf(texto, ens_id, *offsets, leituras, pasta)
            messagebox.showinfo("PDF Gerado", f"Salvo em:\n{pdf}")
        except Exception as e:
            messagebox.showerror("Erro PDF", str(e))

    def _on_email(self):
        try:
            ens_id, texto, leituras, offsets = self._coletar_dados()
            pasta = r"\\servidor\relatorios"
            pdf = gerar_pdf(texto, ens_id, *offsets, leituras, pasta)
            dest = simpledialog.askstring("E-mail", "Digite e-mail do destinatário:")
            if not dest:
                return
            smtp_cfg = {
                "smtp_server": "smtp.exemplo.com",
                "smtp_port": 465,
                "smtp_user":   "usuario@exemplo.com",
                "smtp_pass":   "suasenha"
            }
            enviar_email_com_anexo(
                dest,
                f"Relatório Ensaio {ens_id}",
                "Segue em anexo o relatório em PDF.",
                pdf,
                smtp_cfg
            )
            messagebox.showinfo("E-mail enviado", f"Para: {dest}")
        except Exception as e:
            messagebox.showerror("Erro E-mail", str(e))


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
           
            ("Configurações", lambda: self.load(ConfiguracoesFrame)),
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
    threading.Thread(target=start_serial, daemon=True).start()
    start_serial()
    app = MainApp()
    app.mainloop()
