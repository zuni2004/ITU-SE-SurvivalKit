
public abstract class Duck {// Abstract class Duck, containing fly and quack behavior references
    // References to behavior interfaces

    FlyBehavior flyBehavior;
    QuackBehavior quackBehavior;

    public Duck() {

    }

    // Method to simulate swimming (same for all ducks)
    public void swim() {
        System.out.println("All ducks float, even decoys!");
    }

    // Abstract method display() forces the subclasses to implement it
    public abstract void display();

    public void performFly() {
        flyBehavior.fly();
    }

    public void performQuack() {
        quackBehavior.quack();
    }

    //setters to change the behaviors at runtime when ever i please.
    public void setFlyBehavior(FlyBehavior fb) {
        flyBehavior = fb;
    }

    public void setQuackBehavior(QuackBehavior qb) {
        quackBehavior = qb;
    }
}
