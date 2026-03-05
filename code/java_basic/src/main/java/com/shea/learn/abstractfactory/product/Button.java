package com.shea.learn.abstractfactory.product;

/**
 * 抽象产品A：按钮
 *
 * 为什么用接口？因为不同平台的按钮实现方式完全不同，
 * 它们只共享 "行为契约"，没有共享的实现逻辑。
 */
public interface Button {
    void render();   // 渲染按钮
    void onClick();  // 点击事件
}
