public class DarkRoast extends Beverage {
    public DarkRoast() { // set the appropriate description, “House Blend Coffee,” and then return the
                         // correct cost:
        description = "Dark Roast COffee";
    }

    @Override
    public double cost() {
        return 1.00;
    }
}