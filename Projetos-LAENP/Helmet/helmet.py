import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence

#Converti as classes para frames, para integrar o design 
#Tirei do top level e coloquei em content_frame para ficar melhor a organizção e ficar mais interativo
#Criei uma estrutura com duas áreas principais:
#Um nav_frame que é a área de navegação (o menu lateral) e com todos os votões para acessar as funcionalidades 
#E em segundo o content_frame, que é a área de conteúdo onde as telas para funcionalidades serão carregadas 
#Troquei para o gerenciador grid ao invés do pack para termos um maior controle no alinhamento dos widgets
#Defini o padding para um espaçamento melhor e que esteja melhor visualmente 
#Coloquei o ttk.Style pra ficar mais moderno, definindo estilos para o TFrame, TLabel e TButton
#Coloquei cores de fundo também 

#Coloquei cada funcionalidade de uma janelça separada do tk.TopLevel para uma classe derivada de ttk.Frame, que permite que todos os conteúdos sejam carregados de forma dinâmica no content_frame da MainApp
#Todas as funções agora tem botão "Voltar"
#Usei o método show_main_menu() da classe MainApp
#Coloquei no nav_frame botões que, quando apertados, vão chamar o método load_content, assim carregando a funcionalidade correspondente ao content_frame 

#Agora a MainApp irá ter uma interface dividida em duas colunas: Uma pra navegação e outra pro conteúdo 
#Em uso o método do columfigure() e o rowconfigure() para tornar a área de conteúdo responsiva
#Método createnavigation() para definir o menu lateral, com botoes que chamam métodos para carregar as telas
#Usados agora também métodos de limpeza como o clear_content() para remover todos os widgets do content_frame antes de carregar uma nova tela
#E também o load_content: Irá instanciar a classe de conteúdo (passada como parametro) dentro do content_frame 
#O show_main_menu que exibe uma tela inicial ou uma mensagem de  oas vindas 
#Coloquei um fundo uniforme e alguns estilos personalizados pra todos os widgets via o Ttk.Style 

#Mudança nas classes de funcionalidades:

#Atualizei pra utilizar grid pra organizar os widgets
#BOtão "aplicar" em SensorCorrection, botão "Salvar" emç FrictionSetting e em testsetup e testregistration foram colocados mais espaçamentom
#Em senosr monitor, foi usado novamente o grid, como em todas as classses, e um LabelFrame 
#Implementei a exibição de um GIF animado


#Fim das atualizações de design do dia 27/03



class ElevatorAdjustment(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Organizei o frame com o padding e o grid para ficar num layout melhor 
        self.grid(sticky="nsew", padx=20, pady=20)
        self.step = 1
        self.position = tk.IntVar(value=0)
        
        # Este é  o título da funcionalidade
        ttk.Label(self, text="Ajuste Fino do Elevador", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0,10))
        ttk.Label(self, text="Posição (mm):").grid(row=1, column=0, sticky="w")
        ttk.Label(self, textvariable=self.position).grid(row=1, column=1, sticky="w")
        
        ttk.Button(self, text="+1mm", command=self.increment).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self, text="-1mm", command=self.decrement).grid(row=2, column=1, padx=5, pady=5)
        
        # Este é o botão de voltar que adicionei para retornar ao menu principal
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
        # Isto irá carregar para a próxima etapa, que é a test registration
        self.master.master.load_content(TestRegistration)

class TestRegistration(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
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
    def __init__(self, master):
        super().__init__(master)
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
        
        # Esta é a área parea exibição do GIF
        self.image_label = ttk.Label(self)
        self.image_label.grid(row=4, column=0, columnspan=2, pady=10)
        self.display_gif("led_binary.gif")
        
        # Controles para sensores organizados em Label Frame
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
        
        ttk.Button(self, text="Iniciar Teste", command=self.start_test).grid(row=6, column=0, columnspan=2, pady=10)
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
    
    def start_test(self):
        # Irá carregar a configuração para o teste (TestSetup)

        self.master.master.load_content(TestSetup)


# Esta é a classe principal, mas com uma nova estrutura de navegação e uma área de conteúdo


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Software de Ensaio de Capacete")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        
        # Isso configura o estilo
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        self.style.configure("TButton", font=("Helvetica", 10))
        
        # Criei a área para navegação e conteúdo 
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
            ("Ajuste Fino do Elevador", lambda: self.load_content(ElevatorAdjustment)),
            ("Configurar Atrito", lambda: self.load_content(FrictionSetting)),
            ("Monitoramento de Sensores", lambda: self.load_content(SensorMonitor)),
            ("Correção dos Acelerômetros", lambda: self.load_content(SensorCorrection)),
        ]
        for idx, (text, command) in enumerate(nav_buttons, start=1):
            ttk.Button(self.nav_frame, text=text, command=command).grid(row=idx, column=0, pady=5, sticky="ew")
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def load_content(self, content_class):
        self.clear_content()
        # Vai instanciar a classe de conteúdo no content_frame
        content_class(self.content_frame)
    
    def show_main_menu(self):
        self.clear_content()
        # Exibirá a mensagem de boas vindas no menu principal 
        welcome = ttk.Label(self.content_frame, text="Bem-vindo ao Software de Ensaio de Capacete", font=("Helvetica", 14))
        welcome.pack(expand=True)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
