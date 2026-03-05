package com.shea.learn.abstractfactory.factory;

import com.shea.learn.abstractfactory.product.Button;
import com.shea.learn.abstractfactory.product.Checkbox;
import com.shea.learn.abstractfactory.product.TextField;
import com.shea.learn.abstractfactory.product.windows.WindowsButton;
import com.shea.learn.abstractfactory.product.windows.WindowsCheckbox;
import com.shea.learn.abstractfactory.product.windows.WindowsTextField;

/**
 * Windows 工厂：生产一整套 Windows 风格的 UI 组件
 *
 * 设计意图：
 * 所有 Windows 组件的创建集中在这一个工厂里，
 * 保证产出的 Button、TextField、Checkbox 风格一致。
 * 不可能出现 WindowsButton + MacTextField 的混搭。
 */
public class WindowsFactory implements GUIFactory {

    @Override
    public Button createButton() {
        return new WindowsButton();
    }

    @Override
    public TextField createTextField() {
        return new WindowsTextField();
    }

    @Override
    public Checkbox createCheckbox() {
        return new WindowsCheckbox();
    }
}
