CREATE DATABASE IF NOT EXISTS ensaios_capacete;
USE ensaios_capacete;


CREATE TABLE IF NOT EXISTS Empresa (
    id_empresa INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cidade VARCHAR(100),
    pais VARCHAR(100),
    estado VARCHAR(100),
    cnpj VARCHAR(20),
    telefone VARCHAR(20),
    email VARCHAR(100)
);


CREATE TABLE IF NOT EXISTS Contrato (
    id_contrato INT AUTO_INCREMENT PRIMARY KEY,
    id_empresa INT,
    data_contrato DATE NOT NULL,
    prazo INT,                
    valor_servico DECIMAL(10,2),
    data_contato DATE,
    FOREIGN KEY (id_empresa) REFERENCES Empresa(id_empresa)
);


CREATE TABLE IF NOT EXISTS Capacete (
    id_capacete INT AUTO_INCREMENT PRIMARY KEY,
    modelo VARCHAR(100),
    fabricante VARCHAR(100),
    tamanho VARCHAR(50)
);


CREATE TABLE IF NOT EXISTS Ensaio (
    id_ensaio INT AUTO_INCREMENT PRIMARY KEY,
    data_ensaio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_contrato INT,     
    id_capacete INT,    
    FOREIGN KEY (id_contrato) REFERENCES Contrato(id_contrato),
    FOREIGN KEY (id_capacete) REFERENCES Capacete(id_capacete)
);

CREATE TABLE IF NOT EXISTS EnsaioImpacto (
    id_ensaio_impacto INT AUTO_INCREMENT PRIMARY KEY,
    id_ensaio INT NOT NULL,  
    num_amostra VARCHAR(50),
    num_procedimento VARCHAR(50),
    posicao_teste VARCHAR(50),
    condicionamento VARCHAR(50),
    standard_utilizado VARCHAR(50),
    temperatura FLOAT,        
    umidade FLOAT,            
    valor_atrito FLOAT,       
    norma VARCHAR(50),       
    acel_x FLOAT,             
    acel_y FLOAT,            
    acel_z FLOAT,            
    tempo_amostra FLOAT,      
    notas TEXT,               
    FOREIGN KEY (id_ensaio) REFERENCES Ensaio(id_ensaio) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS SaidaDigital (
    id_saida INT AUTO_INCREMENT PRIMARY KEY,
    id_ensaio INT,            
    canal VARCHAR(50),       
    valor BOOLEAN,            
    tempo_ativacao FLOAT,     
    FOREIGN KEY (id_ensaio) REFERENCES Ensaio(id_ensaio) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Relatorio (
    id_relatorio INT AUTO_INCREMENT PRIMARY KEY,
    id_ensaio INT,            
    texto_relatorio TEXT,     
    data_geracao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_ensaio) REFERENCES Ensaio(id_ensaio)
);


CREATE TABLE IF NOT EXISTS Configuracoes (
  id_config INT PRIMARY KEY AUTO_INCREMENT,
  com_port    VARCHAR(10)    NOT NULL DEFAULT 'COM3',
  baud_rate   INT            NOT NULL DEFAULT 9600,
  i2c_addr    VARCHAR(10)    NOT NULL DEFAULT '0x1C',
  offset_x    DOUBLE         NOT NULL DEFAULT 0,
  offset_y    DOUBLE         NOT NULL DEFAULT 0,
  offset_z    DOUBLE         NOT NULL DEFAULT 0
);

INSERT INTO Configuracoes (com_port, baud_rate, i2c_addr, offset_x, offset_y, offset_z)
VALUES ('COM3', 9600, '0x1C', 0, 0, 0);

