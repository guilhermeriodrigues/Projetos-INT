#include <EmonLib.h> //Biblioteca do sensor de tensão ZMPT101B

#define CAL1 211.6 //Este valor deve ser ajustado com o auxílio de um multímetro
#define PIN_TENS A6 //Define o pino do sensor de tensão

EnergyMonitor teste; //Uma instância do sensor de tensão e corrente é criada

void setup(){  
  
  Serial.begin(9600); //Define-se a taxa de 9600 bits por segundo
  teste.voltage(PIN_TENS, CAL1, 1.7); //São os parâmetros: (PINO ANALÓGIO, VALOR DE CALIBRAÇÃO, MUDANÇA DE FASE)
}

void loop(){

  teste.calcVI(17,2000); //São os parâmetros: (17 SEMICICLOS, TEMPO LIMITE PARA FAZER A MEDIÇÃO)  - 17 semiciclos está relacionado a 60Hz
  float tensaorms   = teste.Vrms; //Recebe a tensão eficaz

  Serial.println(tensaorms);
  delay(1000); //Atualização de 1 segundo
}
