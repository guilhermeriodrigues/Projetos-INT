CREATE DATABASE IF NOT EXISTS ensaios_capacetes;
USE ensaios_capacetes;


CREATE TABLE Empresa (
    id_empresa INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cidade VARCHAR(100),
    pais VARCHAR(100),
    estado VARCHAR(100),
    cnpj VARCHAR(20),
    telefone VARCHAR(20),
    email VARCHAR(100)
);



CREATE TABLE Contrato (
    id_contrato INT AUTO_INCREMENT PRIMARY KEY,
    id_empresa INT,
    data_contrato DATE NOT NULL,
    prazo INT,                
    valor_servico DECIMAL(10,2),
    data_contato DATE,
    FOREIGN KEY (id_empresa) REFERENCES Empresa(id_empresa)
);




CREATE TABLE Capacete (
    id_capacete INT AUTO_INCREMENT PRIMARY KEY,
    modelo VARCHAR(100),
    fabricante VARCHAR(100),
    tamanho VARCHAR(50)
);



CREATE TABLE Ensaio (
    id_ensaio INT AUTO_INCREMENT PRIMARY KEY,
    data_ensaio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_contrato INT,     
    id_capacete INT,    
    FOREIGN KEY (id_contrato) REFERENCES Contrato(id_contrato),
    FOREIGN KEY (id_capacete) REFERENCES Capacete(id_capacete)
);


CREATE TABLE EnsaioImpacto (
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



CREATE TABLE SaidaDigital (
    id_saida INT AUTO_INCREMENT PRIMARY KEY,
    id_ensaio INT,           
    canal VARCHAR(50),        
    valor BOOLEAN,            
    tempo_ativacao FLOAT,     
    FOREIGN KEY (id_ensaio) REFERENCES Ensaio(id_ensaio) ON DELETE CASCADE
);



CREATE TABLE Relatorio (
    id_relatorio INT AUTO_INCREMENT PRIMARY KEY,
    id_ensaio INT,            
    texto_relatorio TEXT,     
    data_geracao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_ensaio) REFERENCES Ensaio(id_ensaio)
);
