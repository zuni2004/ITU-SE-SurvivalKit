public abstract class CondimentDecorator extends Beverage {// we need to be interchangeable with a Beverage, so we
                                                           // extend the Beverage class.
    @Override
    public abstract String getDescription();// going to require that the condiment decorators all reimplement the
                                            // getDescription() method.
}