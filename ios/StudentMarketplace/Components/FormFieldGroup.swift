import UIKit

/// A small label, a form field, and an error message stacked vertically.
final class FormFieldGroup: UIStackView {

    let field: UIControl

    private let titleLabel = UILabel()
    private let errorLabel = UILabel()

    /// nil means "no error".
    var errorMessage: String? {
        didSet { updateErrorAppearance() }
    }

    init(label text: String, field: UIControl) {
        self.field = field
        super.init(frame: .zero)

        axis = .vertical
        spacing = 6

        titleLabel.text = text
        titleLabel.font = .preferredFont(forTextStyle: .subheadline)
        titleLabel.adjustsFontForContentSizeCategory = true
        titleLabel.textColor = .secondaryLabel

        // Error text: small, red, wraps onto several lines if needed.
        errorLabel.font = .preferredFont(forTextStyle: .footnote)
        errorLabel.adjustsFontForContentSizeCategory = true
        errorLabel.textColor = .systemRed
        errorLabel.numberOfLines = 0
        errorLabel.isHidden = true
        errorLabel.isAccessibilityElement = false /// VoiceOver reads the error as the field's hint instead

        field.accessibilityLabel = text

        // Clear the error as soon as the user changes the value.
        field.addTarget(self, action: #selector(fieldDidChange), for: [.editingChanged, .valueChanged])

        addArrangedSubview(titleLabel)
        addArrangedSubview(field)
        addArrangedSubview(errorLabel)
    }

    required init(coder: NSCoder) { fatalError("init(coder:) has not been implemented") }

    private func updateErrorAppearance() {
        let hasError = errorMessage != nil

        errorLabel.text = errorMessage
        errorLabel.isHidden = !hasError

        field.layer.borderWidth = hasError ? 1 : 0
        field.layer.borderColor = UIColor.systemRed.cgColor

        // VoiceOver reads this after the field's label and value.
        field.accessibilityHint = errorMessage
    }

    @objc private func fieldDidChange() {
        errorMessage = nil
    }
}
