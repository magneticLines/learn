package abstractfactory.product.mac;

import abstractfactory.product.Button;

/**
 * Mac 产品族 - 按钮
 *
 * Mac 风格的圆角渐变按钮。
 * 和 MacTextField、MacCheckbox 属于同一产品族，风格统一。
 */
public class MacButton implements Button {
    @Override
    public void render() {
        System.out.println("[Mac] 渲染圆角渐变按钮 ◉");
    }

    @Override
    public void onClick() {
        System.out.println("[Mac] 按钮点击 → 发出 'Pop' 音效");
    }
}
