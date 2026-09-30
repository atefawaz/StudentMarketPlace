import UIKit

/// Form to create a new marketplace listing.
class CreateItemViewController: UIViewController {
    
    // MARK: - UI
    
    private let scrollView = UIScrollView()
    private let formStack = UIStackView()
    
    private let titleField = FormTextField(placeholder: "e.g. Vintage road bike")
    private let descriptionField = FormTextField(placeholder: "Describe your item")
    private let priceField = FormTextField(placeholder: "0.00")
    private let categoryField = FormDropdownField(placeholder: "Select a category", options: ItemCategoryOptions.allCases.map(\.rawValue))
    private let sellerField = FormTextField(placeholder: "Your name")
    private let submitButton = UIButton(type: .system)
    
    /// Each group = label + field + error message.
    /// `lazy` lets these use the fields declared above.
    private lazy var titleGroup = FormFieldGroup(label: "Title", field: titleField)
    private lazy var descriptionGroup = FormFieldGroup(label: "Description", field: descriptionField)
    private lazy var priceGroup = FormFieldGroup(label: "Price", field: priceField)
    private lazy var categoryGroup = FormFieldGroup(label: "Category", field: categoryField)
    private lazy var sellerGroup = FormFieldGroup(label: "Seller Name", field: sellerField)
    
    /// In the order they appear on screen.
    private var allGroups: [FormFieldGroup] {
        [titleGroup, descriptionGroup, priceGroup, categoryGroup, sellerGroup]
    }
    
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
        formStack.axis = .vertical
        formStack.spacing = 20
        formStack.translatesAutoresizingMaskIntoConstraints = false
        allGroups.forEach { formStack.addArrangedSubview($0) }
        formStack.addArrangedSubview(submitButton)
        formStack.setCustomSpacing(32, after: sellerGroup) /// add space before the button

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
    
    private func addKeyboardDismissal() {
        let tap = UITapGestureRecognizer(target: self, action: #selector(dismissKeyboard))
        tap.cancelsTouchesInView = false /// taps still reach buttons and fields
        scrollView.addGestureRecognizer(tap)
    }
    
    // MARK - Submission Helpers
    
    private func setLoading(_ isLoading: Bool) {
        submitButton.isEnabled = !isLoading
        submitButton.configuration?.showsActivityIndicator = isLoading
        submitButton.configuration?.title = isLoading ? "Submitting…" : "Submit"
    }
    
    private func showErrorAlert(for error: Error) {
        let message: String

        if error is URLError {
            message = "Check your internet connection and try again."
        } else {
            message = "Something went wrong while saving your item. Please try again."
        }

        let alert = UIAlertController(title: "Couldn't Create Item", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
    
    // MARK - Actions
    
    @objc private func dismissKeyboard() {
        view.endEditing(true)
    }
    
    @objc private func submitItem() {
        view.endEditing(true)

        // Read the values.
        let title = titleField.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let description = descriptionField.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let category = categoryField.selectedOption ?? ""
        let seller = sellerField.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let price = Decimal(
            string: priceField.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? "",
            locale: .current
        ) ?? 0

        // Validate: a message means "invalid", nil means "OK".
        titleGroup.errorMessage = title.isEmpty ? "Enter a title." : nil
        priceGroup.errorMessage = price > 0 ? nil : "Enter a price greater than 0."
        categoryGroup.errorMessage = category.isEmpty ? "Choose a category." : nil
        sellerGroup.errorMessage = seller.isEmpty ? "Enter your name." : nil

        // If something is wrong, point the user to the first problem and stop.
        if let firstInvalid = allGroups.first(where: { $0.errorMessage != nil }) {
            view.layoutIfNeeded() /// make sure the new error labels have their size
            
            let rect = firstInvalid.convert(firstInvalid.bounds, to: scrollView)
            scrollView.scrollRectToVisible(rect, animated: true)

            UINotificationFeedbackGenerator().notificationOccurred(.error)
            UIAccessibility.post(notification: .layoutChanged, argument: firstInvalid.field)
            return
        }
        
        let request: CreateItemRequest = CreateItemRequest(
            title: title,
            description: description == "" ? nil : description,
            price: NSDecimalNumber(decimal: price).doubleValue,
            category: category,
            imageUrl: nil,
            sellerName: seller
        )
        
        setLoading(true)
        
        APIClient.createItem(request) {
            [weak self] result in
            /// URLSession calls this on a background thread. UI updates must happen on the main thread.
            DispatchQueue.main.async {
                /// the screen was closed while the request was running/
                guard let self else { return }
                
                self.setLoading(false)
                
                switch result {
                case .success(let item):
                    self.navigationController?.popViewController(animated: true)
                case .failure(let error):
                    self.showErrorAlert(for: error)
                }
            }
        }
    }
}
