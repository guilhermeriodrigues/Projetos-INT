#include "dht.h"

const int pinoDHT11 = A1;
const int pinoLDR = A0;

dht DHT;

// Ajuste esses coeficientes conforme a calibração correta
float slope = 1.0; // Inclinação da curva de calibração
float intercept = 0; // Intercepto da curva de calibração
float tempCoefficient = 0.01; // Coeficiente de ajuste para temperatura
float humidityCoefficient = 0.005; // Coeficiente de ajuste para umidade

void setup() {
  Serial.begin(9600);
}

void loop() {
  int valorLDR = analogRead(pinoLDR);
  float tensao = valorLDR * (5.0 / 1024.0);
  float irradiacaoBase = calculateIrradiance(valorLDR); // Nova função de cálculo da irradiância base

  DHT.read11(pinoDHT11);
  float temperatura = DHT.temperature;
  float umidade = DHT.humidity;

  float irradiacaoAjustada = adjustIrradiance(irradiacaoBase, temperatura, umidade);

  Serial.print("Valor LDR: ");
  Serial.print(valorLDR);
  Serial.print(" / Irradiação solar: ");
  Serial.print(irradiacaoAjustada);
  Serial.print(" W/m²");
  Serial.print(" / Umidade: ");
  Serial.print(umidade);
  Serial.print("%");
  Serial.print(" / Temperatura: ");
  Serial.print(temperatura, 0);
  Serial.println("°C");

  delay(2000);
}

float calculateIrradiance(int valorLDR) {
  // Ajuste a fórmula com base em dados de calibração reais
  // Exemplo de fórmula linear básica, ajuste conforme necessário
  float irradiancia = (1023.0 - valorLDR) * (1000.0 / (1023.0 - 50.0)); // Fórmula original
  // float irradiancia = 2976.6 * exp(-17.73 * (valorLDR * (5.0 / 1024.0))); // Outra fórmula possível

  // Esta fórmula deve ser ajustada para refletir os dados de calibração reais
  // Por exemplo, se a relação for linear ou exponencial, ajuste os coeficientes
  return irradiancia;
}

float adjustIrradiance(float irradiancia, float temperatura, float umidade) {
  // Ajuste da irradiância com base na temperatura e umidade
  float irradiacaoAjustada = irradiancia - (tempCoefficient * (temperatura - 25)) - (humidityCoefficient * umidade);
  return irradiacaoAjustada;
}

