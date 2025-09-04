
public class Main {

    public static void main(String[] args) {
        // Create a MallardDuck object using polymorphism rules and for all the rest of the ducks
        Duck mallardDuck = new MallardDuck();
        mallardDuck.display();
        mallardDuck.performFly();
        mallardDuck.performQuack();
        System.out.println();

        Duck rubberDuck = new RubberDuck();
        rubberDuck.display();
        rubberDuck.performFly();
        rubberDuck.performQuack();
        System.out.println();

        Duck redheadDuck = new RedheadDuck();
        redheadDuck.display();
        redheadDuck.performFly();
        redheadDuck.performFly();
        System.out.println();

        Duck decoyDuck = new DecoyDuck();
        decoyDuck.display();
        decoyDuck.performFly();
        decoyDuck.performQuack();
        System.out.println();

        System.out.println("Implementing a new Fly Behaviour to Decoy Duck.");
        decoyDuck.setFlyBehavior(new FlyRocketPowered());//sets a new fly behavior at runtime, over riding it.
        decoyDuck.performFly();
    }
}
