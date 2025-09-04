// Abstract Factory
interface PizzaIngredientFactory {
    Dough createDough();

    Sauce createSauce();

    Cheese createCheese();
}

// Concrete Factories
class NYPizzaIngredientFactory implements PizzaIngredientFactory {
    @Override
    public Dough createDough() {
        return new ThinCrustDough();
    }

    @Override
    public Sauce createSauce() {
        return new MarinaraSauce();
    }

    @Override
    public Cheese createCheese() {
        return new ReggianoCheese();
    }
}

class ChicagoPizzaIngredientFactory implements PizzaIngredientFactory {
    @Override
    public Dough createDough() {
        return new ThickCrustDough();
    }

    @Override
    public Sauce createSauce() {
        return new PlumTomatoSauce();
    }

    @Override
    public Cheese createCheese() {
        return new MozzarellaCheese();
    }
}

// Abstract Products
interface Dough {
    String toString();
}

interface Sauce {
    String toString();
}

interface Cheese {
    String toString();
}

// Concrete Products
class ThinCrustDough implements Dough {
    public String toString() {
        return "Thin Crust Dough";
    }
}

class ThickCrustDough implements Dough {
    public String toString() {
        return "Thick Crust Dough";
    }
}

class MarinaraSauce implements Sauce {
    public String toString() {
        return "Marinara Sauce";
    }
}

class PlumTomatoSauce implements Sauce {
    public String toString() {
        return "Plum Tomato Sauce";
    }
}

class ReggianoCheese implements Cheese {
    public String toString() {
        return "Reggiano Cheese";
    }
}

class MozzarellaCheese implements Cheese {
    public String toString() {
        return "Mozzarella Cheese";
    }
}

// Client Code
class Pizza {
    String name;
    Dough dough;
    Sauce sauce;
    Cheese cheese;

    void prepare() {
        System.out.println("Preparing " + name);
        System.out.println("Tossing " + dough);
        System.out.println("Adding " + sauce);
        System.out.println("Adding " + cheese);
    }

    void bake() {
        System.out.println("Baking " + name);
    }

    void cut() {
        System.out.println("Cutting " + name);
    }

    void box() {
        System.out.println("Boxing " + name);
    }
}

class CheesePizza extends Pizza {
    PizzaIngredientFactory ingredientFactory;

    public CheesePizza(PizzaIngredientFactory ingredientFactory) {
        this.ingredientFactory = ingredientFactory;
    }

    @Override
    void prepare() {
        name = "Cheese Pizza";
        dough = ingredientFactory.createDough();
        sauce = ingredientFactory.createSauce();
        cheese = ingredientFactory.createCheese();
        super.prepare();
    }
}

// Main
public class Main {
    public static void main(String[] args) {
        PizzaIngredientFactory nyFactory = new NYPizzaIngredientFactory();
        Pizza pizza = new CheesePizza(nyFactory);
        pizza.prepare();
        pizza.bake();
        pizza.cut();
        pizza.box();

        PizzaIngredientFactory chicagoFactory = new ChicagoPizzaIngredientFactory();
        pizza = new CheesePizza(chicagoFactory);
        pizza.prepare();
        pizza.bake();
        pizza.cut();
        pizza.box();
    }
}