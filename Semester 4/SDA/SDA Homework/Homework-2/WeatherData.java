
// import java.util.ArrayList;
// import java.util.List;

// public class WeatherData implements Subject {

//     private List<Observer> observers;
//     private float temperature;
//     private float humidity;
//     private float pressure;

//     public WeatherData() {
//         observers = new ArrayList<Observer>(); //holds the new added observers
//     }

//     @Override
//     public void registerObserver(Observer o) {
//         observers.add(o); // adds a new observer at the end of the list
//     }

//     @Override
//     public void removeObserver(Observer o) {
//         observers.remove(o); // removes a new observer at the end of the list
//     }

//     @Override
//     public void notifyObservers() {
//         for (Observer observer : observers) {  //this will access the observers one by one and implement the update() method and notify them
//             observer.update(temperature, humidity, pressure);
//         }
//     }

//     //setter for setting the new measurements
//     public void setMeasurements(float temperature, float humidity, float pressure) {
//         this.temperature = temperature;
//         this.humidity = humidity;
//         this.pressure = pressure;
//         measurementsChanged();
//     }
    
//     //getters of the private variables
//     public float getTemperature() {
//         return temperature;
//     }

//     public float getHumidity() {
//         return humidity;
//     }

//     public float getPressure() {
//         return pressure;
//     }

//     public void measurementsChanged() { //calls the notify method, if the values are changed in the setter than this is called
//         notifyObservers();
//     }
// }
