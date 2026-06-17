package com.shea.learn.abstractfactory.product.mac;

import com.shea.learn.abstractfactory.product.Checkbox;

/**
 * Mac 产品族 - 复选框
 */
public class MacCheckbox implements Checkbox {
    @Override
    public void render() {
        System.out.println("[Mac] 渲染圆形开关样式复选框 ◎");
    }

    @Override
    public boolean isChecked() {
        return true;
    }
}
