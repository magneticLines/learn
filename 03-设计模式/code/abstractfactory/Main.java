package abstractfactory;

import abstractfactory.factory.GUIFactory;
import abstractfactory.factory.MacFactory;
import abstractfactory.factory.WindowsFactory;

/**
 * 启动入口：根据操作系统选择工厂
 *
 * "选择哪个工厂" 的逻辑只在这里出现一次！
 * 整个应用的其他地方都不需要关心平台差异。
 *
 * 运行结果：
 *
 * 在 Windows 上：
 * ====== 渲染 UI 界面 ======
 * [Windows] 渲染扁平化方形按钮 □
 * [Windows] 渲染带边框的文本框 ▭
 * [Windows] 渲染方形复选框 ☑
 * ========================
 * [Windows] 按钮点击 → 发出 'Click' 音效
 *
 * 在 Mac 上：
 * ====== 渲染 UI 界面 ======
 * [Mac] 渲染圆角渐变按钮 ◉
 * [Mac] 渲染无边框圆角文本框 ▢
 * [Mac] 渲染圆形开关样式复选框 ◎
 * ========================
 * [Mac] 按钮点击 → 发出 'Pop' 音效
 */
public class Main {

    public static void main(String[] args) {
        // 根据操作系统属性自动选择工厂
        String osName = System.getProperty("os.name").toLowerCase();
        GUIFactory factory;

        if (osName.contains("windows")) {
            factory = new WindowsFactory();
        } else if (osName.contains("mac")) {
            factory = new MacFactory();
        } else {
            // 默认使用 Windows 工厂演示
            System.out.println("⚠️ 未识别的操作系统: " + osName + "，使用 Windows 工厂演示");
            factory = new WindowsFactory();
        }

        System.out.println("当前操作系统: " + System.getProperty("os.name"));
        System.out.println("选择的工厂: " + factory.getClass().getSimpleName());
        System.out.println();

        // 把工厂注入应用 —— 应用内部不再关心平台
        Application app = new Application(factory);
        app.renderUI();
        app.simulateClick();

        System.out.println();
        System.out.println("文本框值: " + app.getTextFieldValue());
        System.out.println("复选框状态: " + (app.isCheckboxChecked() ? "已选中 ✅" : "未选中 ☐"));

        System.out.println();
        System.out.println("═══════════════════════════════════════");
        System.out.println("  演示：切换到另一个工厂，整套 UI 风格全变");
        System.out.println("═══════════════════════════════════════");
        System.out.println();

        // 切换到 Mac 工厂演示
        GUIFactory anotherFactory = new MacFactory();
        Application app2 = new Application(anotherFactory);
        app2.renderUI();
        app2.simulateClick();
    }
}
