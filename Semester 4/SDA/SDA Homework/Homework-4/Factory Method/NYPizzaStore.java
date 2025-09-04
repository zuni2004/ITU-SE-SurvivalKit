public class NYPizzaStore extends PizzaStore {// Concrete class for New York-style Pizza Store

    @Override
    public Pizza createPizza(String item) {        // Creates and returns the corresponding pizza type
        if (item.equals("cheese")) {
            return new NYStyleCheesePizza();
        } else if (item.equals("veggie")) {
            return new NYStyleVeggiePizza();
        } else if (item.equals("clam")) {
            return new NYStyleClamPizza();
        } else if (item.equals("pepperoni")) {
            return new NYStylePepperoniPizza();
        } else
            return null;
    }
}
