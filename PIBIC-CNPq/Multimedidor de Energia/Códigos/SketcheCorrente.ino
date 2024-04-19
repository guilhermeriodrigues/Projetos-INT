#include <EmonLib.h> //Biblioteca do sensor de tensão ZMPT101B
#include <SPI.h> //Biblioteca ref. ao sensor de corrente elétrica SCT-013-03060
#define CAL2 0 //Este valor deve ser ajustado com o auxílio de um outro instrumento
#define PIN_CORR A7 //Define o pino do sensor de corrente

EnergyMonitor teste; //Uma instância do sensor de tensão e corrente é criada

void setup(){  
  
  Serial.begin(9600); //Define-se a taxa de 9600 bits por segundo
  teste.current(PIN_CORR, CAL2); //São os parâmetros: (PINO ANALÓGIO, VALOR DE CALIBRAÇÃO)
}

void loop(){
  
  teste.calcVI(17,500); //São os parâmetros: (17 SEMICICLOS, TEMPO LIMITE PARA FAZER A MEDIÇÃO)  - 17 semiciclos está relacionado a 60Hz
  float correnterms = teste.Irms; //Recebe o valor da corrente eficaz

  Serial.println(correnterms);
  
}
