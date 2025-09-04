import java.util.ArrayList;
import java.util.List;
// Abstract class representing a Pizza

public abstract class Pizza {
    String name;
    String dough;
    String sauce;
    List<String> toppings = new ArrayList<String>();// List of toppings

    public String getName() {    // Getter for pizza name
        return name;
    }

    public void prepare() {    // Preparing the pizza step by step
        System.out.println("1. " + name + " Pizza is being prepared\n");
        System.out.println("     Tossing dough...");
        System.out.println("     Adding sauce...");
        System.out.println("     Adding toppings: ");
        for (String topping : toppings) {
            System.out.println("     " + topping + "\n");
        }
    }

    public void bake() {
        System.out.println("2. Pizza is being baked\n");
    }

    public void cut() {
        System.out.println("3. Pizza is being cut\n");
    }

    public void box() {
        System.out.println("4. Pizza is being boxed\n");
    }
}
