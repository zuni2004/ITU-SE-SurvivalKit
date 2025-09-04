=> Description
This project simulates various duck behaviors using the Strategy Design Pattern. 
It includes different types of ducks (e.g., MallardDuck, RubberDuck, RedheadDuck, DecoyDuck) and allows you to test their flying and quacking abilities. 
The behavior can be modified dynamically at runtime.

==> FILES INCLUDED:
- Duck.java: Abstract class for all ducks.
- FlyBehavior.java: Interface for flying behavior.
- FlyWithWings.java: Concrete flying behavior (flying with wings).
- FlyNoWay.java: Concrete flying behavior (can't fly).
- FlyRocketPowered.java: Concrete flying behavior (rocket-powered flight).
- QuackBehavior.java: Interface for quacking behavior.
- Quack.java: Concrete quacking behavior (quack).
- MuteQuack.java: Concrete quacking behavior (no sound).
- Squeak.java: Concrete quacking behavior (squeak).
- RubberDuck.java: Concrete duck (RubberDuck) class.
- MallardDuck.java: Concrete duck (MallardDuck) class.
- DecoyDuck.java: Concrete duck (DecoyDuck) class.
- RedheadDuck.java: Concrete duck (RedheadDuck) class.
- MiniDuckSimulator.java: Main class to simulate different duck behaviors.

==> IMPLEMENTATION OF CODE
- Define Behaviors:
We define different flying and quacking behaviors, like FlyWithWings, FlyNoWay, Quack, Squeak, etc. These are interfaces implemented in separate classes.
Encapsulate Behaviors:
Instead of hardcoding behaviors in the Duck classes, we create separate classes for each behavior. For example, FlyWithWings implements FlyBehavior. This makes it easy for us to swap behaviors.
- Use Composition in Duck:
The Duck class holds references to behavior objects (FlyBehavior and QuackBehavior). Each concrete duck uses these behaviors, like MallardDuck flying with wings or RubberDuck squeaking.
Change Behavior at Runtime:
We can change a duck's behavior while the program is running. For example, we can make a DecoyDuck fly with rockets by changing its flying behavior dynamically.

==> HOW I COMPILED AND RUN THE CODE:
1. Open a terminal/command prompt.
2. Navigate to the directory where all `.java` files are located.
3. Compile the Java files using the following command: javac *.java
4. Than using java Main and Enter you will see the display
5. This is my display

zuni_2004@DESKTOP-16K3I1B:/mnt/d/University/SDA/SDA Homework/Homework-1$ javac *.java
zuni_2004@DESKTOP-16K3I1B:/mnt/d/University/SDA/SDA Homework/Homework-1$ java Main
I am a Mallard Duck.
I'm flying with wings!
Quacking.

I am a Rubber Duck.
I can't fly because I have no wings.
Squeaking.

I am a Redhead Duck.
I'm flying with wings!
I'm flying with wings!

I am a Decoy Duck.
I can't fly because I have no wings.
Silence because can't quack.

Implementing a new Fly Behaviour to Decoy Duck.
I can fly with rocket power.
zuni_2004@DESKTOP-16K3I1B:/mnt/d/University/SDA/SDA Homework/Homework-1$