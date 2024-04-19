
// Definição das bibliotecas para o sensor sonda de temperatura

#include <OneWire.h>
#include <DallasTemperature.h>

#define PIN_SONDA 30;

OneWire onewire(PIN_SONDA);
DallasTemperature sonda(&onewire);
DeviceAddress endereco;

void setup() {
  Serial.begin(9600);
  sonda.begin();

}

void loop() {

  if(!sonda.getAddress(endereco,0)){
    Serial.println("Conexão inexistente!");
  }else{
sonda.requestTemperatures();
float temperatura = sonda.getTempC(endereco);
Serial.println(temperatura, 1);
  }
  
}
