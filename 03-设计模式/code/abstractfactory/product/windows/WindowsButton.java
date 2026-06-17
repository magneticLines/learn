package abstractfactory.product.windows;

import abstractfactory.product.Button;

/**
 * Windows 产品族 - 按钮
 *
 * Windows 风格的扁平化方形按钮。
 * 和 WindowsTextField、WindowsCheckbox 属于同一产品族，风格统一。
 */
public class WindowsButton implements Button {
    @Override
    public void render() {
        System.out.println("[Windows] 渲染扁平化方形按钮 □");
    }

    @Override
    public void onClick() {
        System.out.println("[Windows] 按钮点击 → 发出 'Click' 音效");
    }
}
