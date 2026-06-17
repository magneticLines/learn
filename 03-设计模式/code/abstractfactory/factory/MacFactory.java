package abstractfactory.factory;

import abstractfactory.product.Button;
import abstractfactory.product.Checkbox;
import abstractfactory.product.TextField;
import abstractfactory.product.mac.MacButton;
import abstractfactory.product.mac.MacCheckbox;
import abstractfactory.product.mac.MacTextField;

/**
 * Mac 工厂：生产一整套 Mac 风格的 UI 组件
 */
public class MacFactory implements GUIFactory {

    @Override
    public Button createButton() {
        return new MacButton();
    }

    @Override
    public TextField createTextField() {
        return new MacTextField();
    }

    @Override
    public Checkbox createCheckbox() {
        return new MacCheckbox();
    }
}
