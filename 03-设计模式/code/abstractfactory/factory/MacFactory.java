package com.shea.learn.abstractfactory.factory;

import com.shea.learn.abstractfactory.product.Button;
import com.shea.learn.abstractfactory.product.Checkbox;
import com.shea.learn.abstractfactory.product.TextField;
import com.shea.learn.abstractfactory.product.mac.MacButton;
import com.shea.learn.abstractfactory.product.mac.MacCheckbox;
import com.shea.learn.abstractfactory.product.mac.MacTextField;

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
