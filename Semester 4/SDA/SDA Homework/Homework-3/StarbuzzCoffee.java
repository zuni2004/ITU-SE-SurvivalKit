public class StarbuzzCoffee {
    public static void main(String[] args) {
        Beverage beverage1 = new DarkRoast();
        beverage1 = new Milk(beverage1);
        beverage1 = new Mocha(beverage1);
        System.out.println(beverage1.getDescription() + " $" + beverage1.cost());

        Beverage beverage2 = new HouseBlend();
        beverage2 = new Soy(beverage2);
        beverage2 = new Whip(beverage2);
        System.out.println(beverage2.getDescription() + " $" + beverage2.cost());

        Beverage beverage3 = new Espresso();
        beverage3 = new Whip(beverage3);
        System.out.println(beverage3.getDescription() + " $" + beverage3.cost());

        Beverage beverage4 = new Decaf();
        beverage4 = new Mocha(beverage4);
        System.out.println(beverage4.getDescription() + " $" + beverage4.cost());
    }
}
