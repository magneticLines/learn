package abstractfactory.product;

/**
 * 抽象产品B：文本框
 */
public interface TextField {
    void render();       // 渲染文本框
    String getValue();   // 获取输入值
}
