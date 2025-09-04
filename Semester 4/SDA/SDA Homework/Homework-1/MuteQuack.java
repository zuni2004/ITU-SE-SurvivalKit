
public class MuteQuack implements QuackBehavior {

    @Override
    public void quack() {
        System.out.println("Silence because can't quack.");
    }
}
