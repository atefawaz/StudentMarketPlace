import UIKit

/// A text field with a rounded system-colored background and inner padding.
public final class FormTextField: UITextField {
    
    private let horizontalPadding: CGFloat = 14
    private let verticalPadding: CGFloat = 12
    
    /// A secondary, supporting initializer
    convenience init(placeholder: String) {
        self.init(frame: .zero)
        self.placeholder = placeholder
        backgroundColor = .secondarySystemBackground
        textColor = .label
        font = .preferredFont(forTextStyle: .body)
        adjustsFontForContentSizeCategory = true
        clearButtonMode = .whileEditing
        layer.cornerRadius = 10
        layer.cornerCurve = .continuous
    }
    
    /// Height = one line of text + padding, never less than a comfortable 48pt tap target.
    public override var intrinsicContentSize: CGSize {
        let size = super.intrinsicContentSize
        return CGSize(width: size.width, height: max(size.height + 2 * verticalPadding, 48))
    }
    
    /// Inset the text, the placeholder, and the text-while-editing horizontally
    public override func textRect(forBounds bounds: CGRect) -> CGRect {
        super.textRect(forBounds: bounds).insetBy(dx: horizontalPadding, dy: 0)
    }
    
    public override func editingRect(forBounds bounds: CGRect) -> CGRect {
        super.editingRect(forBounds: bounds).insetBy(dx: horizontalPadding, dy: 0)
    }
 
    public override func placeholderRect(forBounds bounds: CGRect) -> CGRect {
        bounds.insetBy(dx: horizontalPadding, dy: 0)
    }
 
    public override func clearButtonRect(forBounds bounds: CGRect) -> CGRect {
        super.clearButtonRect(forBounds: bounds).offsetBy(dx: -8, dy: 0)
    }
}
