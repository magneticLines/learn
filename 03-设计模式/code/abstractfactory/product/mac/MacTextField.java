package abstractfactory.product.mac;

import abstractfactory.product.TextField;

/**
 * Mac 产品族 - 文本框
 */
public class MacTextField implements TextField {
    @Override
    public void render() {
        System.out.println("[Mac] 渲染无边框圆角文本框 ▢");
    }

    @Override
    public String getValue() {
        return "Mac文本框的值";
    }
}
