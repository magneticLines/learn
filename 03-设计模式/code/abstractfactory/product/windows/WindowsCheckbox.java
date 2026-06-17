package com.shea.learn.abstractfactory.product.windows;

import com.shea.learn.abstractfactory.product.Checkbox;

/**
 * Windows 产品族 - 复选框
 */
public class WindowsCheckbox implements Checkbox {
    @Override
    public void render() {
        System.out.println("[Windows] 渲染方形复选框 ☑");
    }

    @Override
    public boolean isChecked() {
        return true;
    }
}
