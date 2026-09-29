import UIKit

public final class FormDropdownField: UIControl {
    
    private let horizontalPadding: CGFloat = 14
    private let placeholderText: String
    private let options: [String]

    private let valueLabel = UILabel()
    private let chevronImageView = UIImageView(image: UIImage(systemName: "chevron.up.chevron.down"))
    private let menuButton = UIButton(type: .system) /// exists only to host the tap + menu
    
    /// nil until the user picks something mirroring an empty field.
    private(set) var selectedOption: String? {
        didSet {
            refresh()
            sendActions(for: .valueChanged)
        }
    }
    
    init(placeholder: String, options: [String]) {
        self.placeholderText = placeholder
        self.options = options
        super.init(frame: .zero)
        configureAppearance()
        refresh()
    }
    
    required init?(coder: NSCoder) { fatalError("init(coder:) has not been implemented") }
    
    private func configureAppearance() {
        backgroundColor = .secondarySystemBackground
        layer.cornerRadius = 10
        layer.cornerCurve = .continuous
        
        valueLabel.font = .preferredFont(forTextStyle: .body)
        valueLabel.adjustsFontForContentSizeCategory = true
        
        chevronImageView.tintColor = .secondaryLabel
        chevronImageView.preferredSymbolConfiguration = UIImage.SymbolConfiguration(pointSize: 13, weight: .semibold)
        chevronImageView.adjustsImageSizeForAccessibilityContentSizeCategory = true
        chevronImageView.setContentHuggingPriority(.required, for: .horizontal)
        chevronImageView.setContentCompressionResistancePriority(.required, for: .horizontal)
        
        menuButton.showsMenuAsPrimaryAction = true
        
        [valueLabel, chevronImageView, menuButton].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
            addSubview($0)
        }
        
        NSLayoutConstraint.activate([
            heightAnchor.constraint(greaterThanOrEqualToConstant: 48),
            
            valueLabel.leadingAnchor.constraint(equalTo: leadingAnchor, constant: horizontalPadding),
            valueLabel.trailingAnchor.constraint(lessThanOrEqualTo: chevronImageView.leadingAnchor, constant: -8),
            valueLabel.centerYAnchor.constraint(equalTo: centerYAnchor),
            valueLabel.topAnchor.constraint(greaterThanOrEqualTo: topAnchor, constant: 12),
            valueLabel.bottomAnchor.constraint(lessThanOrEqualTo: bottomAnchor, constant: -12),

            chevronImageView.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -horizontalPadding),
            chevronImageView.centerYAnchor.constraint(equalTo: centerYAnchor),

            // Covers the whole control: the actual tap target and menu anchor.
            menuButton.topAnchor.constraint(equalTo: topAnchor),
            menuButton.leadingAnchor.constraint(equalTo: leadingAnchor),
            menuButton.trailingAnchor.constraint(equalTo: trailingAnchor),
            menuButton.bottomAnchor.constraint(equalTo: bottomAnchor),
        ])
        
        /// present this as one voiceover element instead of three separate ones
        isAccessibilityElement = true
        accessibilityTraits = .button
        [valueLabel, chevronImageView, menuButton].forEach { $0.isAccessibilityElement = false }
    }
    
    private func refresh() {
        valueLabel.text = selectedOption ?? placeholderText
        valueLabel.textColor = selectedOption == nil ? .placeholderText : .label
        accessibilityValue = selectedOption ?? "Not selected"
        
        /// rebuilding the menu is how you get the checkmark to move to the new selection
        let actions = options.map { option in
            UIAction(title: option, state: option == selectedOption ? .on : .off) { [weak self] _ in self?.selectedOption = option }
        }
        menuButton.menu = UIMenu(options: .singleSelection, children: actions)
    }
}
