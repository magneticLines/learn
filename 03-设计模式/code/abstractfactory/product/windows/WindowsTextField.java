package com.shea.learn.abstractfactory.product.windows;

import com.shea.learn.abstractfactory.product.TextField;

/**
 * Windows 产品族 - 文本框
 */
public class WindowsTextField implements TextField {
    @Override
    public void render() {
        System.out.println("[Windows] 渲染带边框的文本框 ▭");
    }

    @Override
    public String getValue() {
        return "Windows文本框的值";
    }
}
