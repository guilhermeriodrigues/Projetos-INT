#include "EmonLib.h" //Biblioteca do sensor de tensão ZMPT101B
#include <OneWire.h> //Biblioteca do sensor de temperatura tipo sonda DS18B20
#include <DallasTemperature.h> //Biblioteca do sensor de temperatura tipo sonda DS18B20
#include <SPI.h> //Biblioteca ref. ao sensor de corrente elétrica SCT-013-030
#include <Ethernet.h>
#include <Modbus.h>
#include <ModbusIP.h>

#define CAL1 211.6 //Este valor deve ser ajustado com o auxílio de um multímetro
#define CAL2 60 //Este valor deve ser ajustado com o auxílio de um outro instrumento
#define PIN_SONDA 30 //Define o pino da sonda
#define PIN_TENS A6 //Define o pino do sensor de tensão
#define PIN_CORR A7 //Define o pino do sensor de corrente

EnergyMonitor teste; //Uma instância do sensor de tensão e corrente é criada
OneWire onewire(PIN_SONDA); //Uma instância ref. a sonda passando o pino como parâmetro
DallasTemperature sonda(&onewire); // Passa o endereço de onewire

const int sensor1 = 0; //Offset do sensor de tensão
const int sensor2 = 1; //Offset do sensor de corrente
const int sensor3 = 2; //Offset do sensor de temperatura
const int aux1 = 3; //Offset da potência ativa
const int aux2 = 4; //Offset da potência aparente
const int aux3 = 5; //Offset do fator de potência

ModbusIP mb; //Instância do objeto Modbus

void setup(){  

  byte mac[] = {0x01, 0x23, 0xBE, 0xFE, 0xAF, 0xA5}; //Definição do endereço MAC
  byte ip[] = {192,168,1,173} //Definição do endereço IP
  mb.config(mac,ip); //Configurando o Modbus IP

  //Atribuição de Input Register
  mb.addIreg(sensor1);
  mb.addIreg(sensor2);
  
  //Atribuição de Input Status
  mb.addIsts(sensor3);
  
  serial.begin(9600); //Define-se a taxa de 9600 bits por segundo
  teste.voltage(PIN_TENS, CAL1, 1.7); //São os parâmetros: (PINO ANALÓGIO, VALOR DE CALIBRAÇÃO, MUDANÇA DE FASE)
  teste.current(PIN_CORR, CAL2); //São os parâmetros: (PINO ANALÓGIO, VALOR DE CALIBRAÇÃO)
  sonda.begin(); //Inicializa a sonda ao ligar o Arduino
}

void loop(){

  mb.task(); //Loop de atualização do ModbusIP
  
  teste.calcVI(17,2000); //São os parâmetros: (17 SEMICICLOS, TEMPO LIMITE PARA FAZER A MEDIÇÃO)  - 17 semiciclos está relacionado a 60Hz
  sonda.requestTemperatures(); //Solicita o valor da temperatura
  float tensaorms   = teste.Vrms; //Recebe a tensão eficaz
  float temperatura = sonda.getTempCByIndex(0)); //Recebe o valor da temperatura
  float correnterms = teste.Irms //Recebe o valor da corrente eficaz
  float potativa = teste.realPower;
  float potaparente = teste.apparentPower;
  float fp = teste.powerFactor;
  

  //Envio para o ScadaBR

  mb.Ireg(sensor1, tensaorms);
  mb.Ireg(sensor2, correnterms);
  mb.Ists(sensor3, temperatura);
  mb.Ireg(aux1, potativa);
  mb.Ireg(aux2, potaparente);
  mb.Ireg(aux3, fp);
  
  delay(1000); //Atualização de 1 segundo
}
