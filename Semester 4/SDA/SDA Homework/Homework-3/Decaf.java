public class Decaf extends Beverage {
    public Decaf() { // set the appropriate description, “House Blend Coffee,” and then return the
                     // correct cost:
        description = "Decaf COffee";
    }

    @Override
    public double cost() {
        return 1.50;
    }
}