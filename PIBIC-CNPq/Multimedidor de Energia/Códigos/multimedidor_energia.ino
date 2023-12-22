#include "EmonLib.h" //Biblioteca do sensor de tensão ZMPT101B
#include <OneWire.h> //Biblioteca do sensor de temperatura tipo sonda DS18B20
#include <DallasTemperature.h> //Biblioteca do sensor de temperatura tipo sonda DS18B20
#include <SPI.h> //Biblioteca ref. ao sensor de corrente elétrica SCT-013-030

#define CAL1 211.6 //Este valor deve ser ajustado com o auxílio de um multímetro
#define CAL2 60 //Este valor deve ser ajustado com o auxílio de um outro instrumento
#define PIN_SONDA 30 //Define o pino da sonda
#define PIN_TENS A6 //Define o pino do sensor de tensão
#define PIN_CORR A7 //Define o pino do sensor de corrente

EnergyMonitor ddp; //Uma instância do sensor de tensão é criada
EnergyMonitor ca; //Uma instância do sensor de corrente é criada
OneWire onewire(PIN_SONDA); //Uma instância ref. a sonda passando o pino como parâmetro
DallasTemperature sonda(&onewire); // Passa o endereço de onewire

int rede = 220; //Declaração da tensão da rede elétrica

void setup(){  

  serial.begin(9600); //Define-se a taxa de 9600 bits por segundo
  ddp.voltage(PIN_TENS, CAL1, 1.7); //São os parâmetros: (PINO ANALÓGIO, VALOR DE CALIBRAÇÃO, MUDANÇA DE FASE)
  ca.current(PIN_CORR, CAL2); //São os parâmetros: (PINO ANALÓGIO, VALOR DE CALIBRAÇÃO)
  sonda.begin(); //Inicializa a sonda ao ligar o Arduino
}

void loop(){
  
  ddp.calcVI(17,2000); //São os parâmetros: (17 SEMICICLOS, TEMPO LIMITE PARA FAZER A MEDIÇÃO)  - 17 semiciclos está relacionado a 60Hz
  float tensaorms   = ddp.Vrms; //Recebe a tensão eficaz

  sonda.requestTemperatures(); //Solicita o valor da temperatura
  float temperatura = sonda.getTempCByIndex(0)); //Recebe o valor da temperatura

  float correnterms = ca.calcIrms(1480); //Recebe o valor da corrente eficaz

  //Print no terminal

  serial.print("Tensão:"+ String(tensaorms)+" v, corrente: "+String(correnterms)+" A, temperatura:"+String(temperatura)+" °C);
  delay(1000); //Atualização de 1 segundo
}
