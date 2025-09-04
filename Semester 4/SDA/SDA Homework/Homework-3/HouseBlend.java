public class HouseBlend extends Beverage {
    public HouseBlend() { // set the appropriate description, “House Blend Coffee,” and then return the
                          // correct cost:
        description = "House Blend Coffee";
    }

    @Override
    public double cost() {
        return 0.50;
    }
}