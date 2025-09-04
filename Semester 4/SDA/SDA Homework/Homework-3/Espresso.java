public class Espresso extends Beverage {

    public Espresso() {// To take care of the description, we set this in the constructor for the
                       // class. Remember the description instance variable is inherited from Beverage.
        description = "Espresso";
    }

    @Override
    public double cost() {
        return 2.00;
    }
}