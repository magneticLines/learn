package abstractfactory.product;

/**
 * 抽象产品C：复选框
 */
public interface Checkbox {
    void render();         // 渲染复选框
    boolean isChecked();   // 是否选中
}
