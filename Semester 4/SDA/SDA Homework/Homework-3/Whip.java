public class Whip extends CondimentDecorator {
    Beverage beverage; // An instance variable to hold the beverage we are wrapping.

    public Whip(Beverage beverage) {
        this.beverage = beverage; // A way to set this instance variable to the object we are wrapping. Here,
                                  // we’re going to to pass the beverage we’re wrapping to the decorator’s
                                  // constructor.
    }

    @Override
    public String getDescription() {
        return beverage.getDescription() + ", Whip";
    }

    @Override
    public double cost() {
        return .20 + beverage.cost();
    }// we need to compute the cost of our beverage with Mocha. First, we delegate
     // the call to the object we’re decorating, so that it can compute the cost;
}