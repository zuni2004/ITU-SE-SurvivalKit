
// public class StatisticsDisplay implements Observer, DisplayElement { //this one keeps the min/avg/max measurement and displays them

//     private float maxTemp = Float.MIN_VALUE;//took the least smallest float to set to max
//     private float minTemp = Float.MAX_VALUE;//took the max greayet float to set to min
//     private float tempSum = 0;
//     private int numReadings;
//     private WeatherData weatherData;

//     public StatisticsDisplay(WeatherData weatherData) {
//         this.weatherData = weatherData;
//         weatherData.registerObserver(this);
//     }

//     @Override
//     public void update(float temperature, float humidity, float pressure) {
//         tempSum += temperature;
//         numReadings++;
//         if (temperature > maxTemp) {
//             maxTemp = temperature;
//         }
//         if (temperature < minTemp) {
//             minTemp = temperature;
//         }
//         display();
//     }

//     @Override
//     public void display() {
//         System.out.println("Average temperature = " + (tempSum / numReadings));
//         System.out.println("Max Temperature = " + maxTemp);
//         System.out.println("Min Temperature = " + minTemp);
//     }
// }
