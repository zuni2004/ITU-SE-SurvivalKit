
// public class CurrentConditionsDisplay implements Observer, DisplayElement {
// //this class implemennts the Observer interface as the concrete class do it can get changes from the WeatherData object

//     private float temperature;
//     private float humidity;
//     private WeatherData weatherData;

//     public CurrentConditionsDisplay(WeatherData weatherData) {// constructor passes the weatherData object which is the subject and we use it to regerter the display as the oberser
//         this.weatherData = weatherData;
//         weatherData.registerObserver(this);
//     }

//     @Override
//     public void update(float temperature, float humidity, float pressure) {
//         this.temperature = temperature;
//         this.humidity = humidity;
//         display();//when updated displays the newly changed data
//     }

//     @Override
//     public void display() {
//         System.out.println("Current conditions: " + temperature
//                 + "F degrees and " + humidity + "% humidity");
//     }
// }
