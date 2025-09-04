public class PizzaTestDrive {
    public static void main(String[] args) {
        // Create a SimplePizzaFactory
        SimplePizzaFactory factory = new SimplePizzaFactory();

        // Create a PizzaStore and pass the factory to it
        PizzaStore store = new PizzaStore(factory);

        // Order a Cheese Pizza
        Pizza cheesePizza = store.orderPizza("cheese");
        System.out.println("Ordered a " + cheesePizza.getName() + "\n");

        // Order a Pepperoni Pizza
        Pizza pepperoniPizza = store.orderPizza("pepperoni");
        System.out.println("Ordered a " + pepperoniPizza.getName() + "\n");

        // Order a Veggie Pizza
        Pizza veggiePizza = store.orderPizza("veggie");
        System.out.println("Ordered a " + veggiePizza.getName() + "\n");
    }
}