package com.shea.learn.abstractfactory.factory;

import com.shea.learn.abstractfactory.product.Button;
import com.shea.learn.abstractfactory.product.Checkbox;
import com.shea.learn.abstractfactory.product.TextField;

/**
 * 抽象工厂：定义 "创建一整套 UI 组件" 的接口
 *
 * 关键设计意图：
 * 1. 每个方法对应一种产品（createButton、createTextField、createCheckbox）
 * 2. 一个工厂实例会创建一整套风格统一的产品
 * 3. 客户端只依赖这个接口，不依赖任何具体产品类
 *
 * 这和工厂方法的区别：
 * → 工厂方法：一个接口只有一个 createXxx() 方法，创建一种产品
 * → 抽象工厂：一个接口有多个 createXxx() 方法，创建一组配套产品
 */
public interface GUIFactory {
    Button createButton();

    TextField createTextField();

    Checkbox createCheckbox();
}
