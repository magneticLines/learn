package abstractfactory;

import abstractfactory.factory.GUIFactory;
import abstractfactory.product.Button;
import abstractfactory.product.Checkbox;
import abstractfactory.product.TextField;

/**
 * 客户端：Application
 *
 * 注意观察：整个类中没有出现任何 Windows 或 Mac 的具体类名！
 * 它只依赖 GUIFactory、Button、TextField、Checkbox 这些抽象接口。
 *
 * 这意味着：
 * - 传入 WindowsFactory → 所有 UI 都是 Windows 风格
 * - 传入 MacFactory → 所有 UI 都是 Mac 风格
 * - 不可能出现混搭！（因为一个工厂只生产一套风格的产品）
 */
public class Application {

    private Button button;
    private TextField textField;
    private Checkbox checkbox;

    /**
     * 通过构造函数注入抽象工厂。
     * 具体用哪个工厂，由外部（调用方/配置文件/Spring容器）决定。
     */
    public Application(GUIFactory factory) {
        // 用同一个工厂创建所有组件 → 保证风格统一！
        this.button = factory.createButton();
        this.textField = factory.createTextField();
        this.checkbox = factory.createCheckbox();
    }

    /**
     * 渲染整个 UI 界面
     */
    public void renderUI() {
        System.out.println("====== 渲染 UI 界面 ======");
        button.render();
        textField.render();
        checkbox.render();
        System.out.println("========================");
    }

    /**
     * 模拟按钮点击
     */
    public void simulateClick() {
        button.onClick();
    }

    /**
     * 获取文本框的值
     */
    public String getTextFieldValue() {
        return textField.getValue();
    }

    /**
     * 获取复选框状态
     */
    public boolean isCheckboxChecked() {
        return checkbox.isChecked();
    }
}
