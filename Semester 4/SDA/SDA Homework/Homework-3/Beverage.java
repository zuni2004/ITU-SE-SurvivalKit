
public abstract class Beverage {// Beverage is an abstract getDescription is already class with the two methods
                                // implemented for us, but we getDescription() and cost().
    String description = "Unknown Beverage";

    public String getDescription() {
        return description;
    }

    public abstract double cost();
}