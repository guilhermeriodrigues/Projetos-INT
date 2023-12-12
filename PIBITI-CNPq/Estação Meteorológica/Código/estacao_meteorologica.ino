#include <Modbus.h>
#include <ModbusSerial.h>
#include <DHT.h>

// Instância do objeto DHT11

  DHT dht(A1, DHT11);

// Instância do objeto Modbus Serial

  ModbusSerial mb;

// Declaração de variáveis 

  long ts;
  const int var_umid= 1;
  const int var_temp = 2;
  
// Definição dos offsets (0-9999)

void setup(){

  mb.config(&Serial, 9600, SERIAL_8N1);

// Serial 8N1 - 8 bits de pacote, sem paridade e bits de stop de tamanho unitário
// Configuração do Modbus RTU com taxa de trasmissão de 9600 bits por segundo.

  mb.setSlaveId(1);

// Definição de um ID de 1 até 247 para o datasource

  mb.addIreg(var_temp);
  mb.addIreg(var_umid);


// Inicialização da contagem do tempo e do DHT11 

    dht.begin();
    ts = millis();

}

void loop(){
  
// Método utilizado para leitura do Modbus a cada loop

  mb.task();

// Lê o valor analógico da temperatura e armazena na variável criada a cada 1 segundo

 if (millis() > ts + 1000) {
  mb.Ireg(var_temp, dht.readTemperature());
  mb.Ireg(var_umid, dht.readHumidity());
  ts = millis();
 }

}
