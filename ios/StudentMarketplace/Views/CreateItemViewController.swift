import UIKit

/// Form to create a new marketplace listing.
///
/// TODO: Make the category field a dropdown field
/// TODO: Validate that required fields are not empty and price > 0.
/// TODO: POST the new item using APIClient.createItem().
/// TODO: On success, pop back to the list. On error, show an alert.
class CreateItemViewController: UIViewController {
    
    // MARK: - UI
    
    private let scrollView = UIScrollView()
    private let formStack = UIStackView()
    
    private let titleField = FormTextField(placeholder: "e.g. Vintage road bike")
    private let descriptionField = FormTextField(placeholder: "Describe your item")
    private let priceField = FormTextField(placeholder: "0.00")
    private let categoryField = FormTextField(placeholder: "e.g. Sports")
    private let sellerField = FormTextField(placeholder: "Your name")
    private let submitButton = UIButton(type: .system)
    
    /// The order the "Next" key walks through the fields.
    private lazy var orderedFields: [UITextField] = [
        titleField, descriptionField, priceField, categoryField, sellerField
    ]
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Sell an Item"
        view.backgroundColor = .systemBackground
        
        configureFields()
        configureSubmitButton()
        layoutForm()
        addKeyboardDismissal()
    }
    
    // MARK - Configuration
    
    private func configureFields() {
        titleField.autocapitalizationType = .sentences
        
        descriptionField.autocapitalizationType = .sentences
        
        priceField.keyboardType = .decimalPad   /// digits and a decimal separator only
        
        categoryField.autocapitalizationType = .words
        
        sellerField.autocapitalizationType = .words
        sellerField.autocorrectionType = .no
        sellerField.textContentType = .name     /// lets iOS suggest the user's name
    }
    
    private func configureSubmitButton() {
        var config = UIButton.Configuration.filled() /// uses the app's tint color automatically
        config.title = "Submit"
        config.cornerStyle = .large
        config.buttonSize = .large
        submitButton.configuration = config
        submitButton.addTarget(self, action: #selector(submitItem), for: .touchUpInside)
    }
    
    // MARK - Layout
    
    private func layoutForm() {
        /// Each group is a small label sitting above its text field.
        let groups = [
            makeGroup(label: "Title", field: titleField),
            makeGroup(label: "Description", field: descriptionField),
            makeGroup(label: "Price", field: priceField),
            makeGroup(label: "Category", field: categoryField),
            makeGroup(label: "Seller Name", field: sellerField),
        ]
        
        formStack.axis = .vertical
        formStack.spacing = 20
        formStack.translatesAutoresizingMaskIntoConstraints = false
        (groups + [submitButton]).forEach { formStack.addArrangedSubview($0) }
        formStack.setCustomSpacing(32, after: groups.last!) /// add space before the button
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.alwaysBounceVertical = true
        scrollView.keyboardDismissMode = .interactive
        scrollView.addSubview(formStack)
        view.addSubview(scrollView)
        
        NSLayoutConstraint.activate([
            /// Scroll view fills the screen, but stops above the keyboard when it appears.
            scrollView.topAnchor.constraint(equalTo: view.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.keyboardLayoutGuide.topAnchor),
            
            /// Content is exactly as wide as the scroll view: vertical scrolling only.
            scrollView.contentLayoutGuide.widthAnchor.constraint(equalTo: scrollView.frameLayoutGuide.widthAnchor),
            
            /// The stack defines the scrollable height.
            formStack.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor, constant: 24),
            formStack.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor, constant: -24),
            
            /// Readable margins: respects notches/safe areas and caps the width on iPad.
            formStack.leadingAnchor.constraint(equalTo: view.readableContentGuide.leadingAnchor),
            formStack.trailingAnchor.constraint(equalTo: view.readableContentGuide.trailingAnchor),
        ])
    }
    
    private func makeGroup(label text: String, field: UITextField) -> UIStackView {
        let label = UILabel()
        label.text = text
        label.font = .preferredFont(forTextStyle: .subheadline)
        label.adjustsFontForContentSizeCategory = true
        label.textColor = .secondaryLabel
        
        field.accessibilityLabel = text
        
        let group = UIStackView(arrangedSubviews: [label, field])
        group.axis = .vertical
        group.spacing = 6
        return group
    }
    
    private func addKeyboardDismissal() {
        let tap = UITapGestureRecognizer(target: self, action: #selector(dismissKeyboard))
        tap.cancelsTouchesInView = false /// taps still reach buttons and fields
        scrollView.addGestureRecognizer(tap)
    }
    
    // MARK - Actions
    
    @objc private func dismissKeyboard() {
        view.endEditing(true)
    }
    
    @objc private func submitItem() {
        // TODO: read the field values, validate them, and create the item.
        view.endEditing(true)
        
        let title = titleField.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let description = descriptionField.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let category = categoryField.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let seller = sellerField.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        
        let price = Decimal(
            string: priceField.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? "",
            locale: .current
        ) ?? 0
        
        print("title: ", title)
        print("description: ", description)
        print("priceText: ", price)
        print("category: ", category)
        print("seller: ", seller)
    }
}

// MARK - FormTextField

/// A text field with a rounded system-colored background and inner padding.
private final class FormTextField: UITextField {
    
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
    override var intrinsicContentSize: CGSize {
        let size = super.intrinsicContentSize
        return CGSize(width: size.width, height: max(size.height + 2 * verticalPadding, 48))
    }
    
    /// Inset the text, the placeholder, and the text-while-editing horizontally
    override func textRect(forBounds bounds: CGRect) -> CGRect {
        super.textRect(forBounds: bounds).insetBy(dx: horizontalPadding, dy: 0)
    }
    
    override func editingRect(forBounds bounds: CGRect) -> CGRect {
        super.editingRect(forBounds: bounds).insetBy(dx: horizontalPadding, dy: 0)
    }
 
    override func placeholderRect(forBounds bounds: CGRect) -> CGRect {
        bounds.insetBy(dx: horizontalPadding, dy: 0)
    }
 
    override func clearButtonRect(forBounds bounds: CGRect) -> CGRect {
        super.clearButtonRect(forBounds: bounds).offsetBy(dx: -8, dy: 0)
    }
}
