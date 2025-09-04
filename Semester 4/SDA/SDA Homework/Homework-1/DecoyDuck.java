
public class DecoyDuck extends Duck {

    public DecoyDuck() {//constructor calls behaviors to override
        flyBehavior = new FlyNoWay();
        quackBehavior = new MuteQuack();
    }

    @Override
    public void display() {
        System.out.println("I am a Decoy Duck.");
    }
}
