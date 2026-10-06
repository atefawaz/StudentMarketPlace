import UIKit

/// Compact, tappable card summarising an `Item`.
final class ItemCardView: UIControl {

    let item: Item

    private let titleLabel = UILabel()
    private let soldLabel = UILabel()
    private let priceLabel = UILabel()

    init(item: Item) {
        self.item = item
        super.init(frame: .zero)
        setup()
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) { fatalError("init(coder:) is not supported") }

    override var isHighlighted: Bool {
        didSet { UIView.animate(withDuration: 0.15) { self.alpha = self.isHighlighted ? 0.6 : 1 } }
    }

    private func setup() {
        backgroundColor = .secondarySystemBackground
        layer.cornerRadius = 12
        layer.cornerCurve = .continuous

        titleLabel.text = item.title
        titleLabel.font = .preferredFont(forTextStyle: .headline)
        titleLabel.numberOfLines = 2

        soldLabel.text = "SOLD"
        soldLabel.font = .preferredFont(forTextStyle: .caption1)
        soldLabel.textColor = .systemRed
        soldLabel.isHidden = !item.isSold

        priceLabel.text = item.formattedPrice
        priceLabel.font = .preferredFont(forTextStyle: .subheadline)
        priceLabel.textColor = .secondaryLabel

        [titleLabel, soldLabel, priceLabel].forEach { $0.adjustsFontForContentSizeCategory = true }

        // Flexible spacer keeps the price aligned at the bottom across cards of equal height.
        let spacer = UIView()
        spacer.setContentHuggingPriority(.defaultLow - 1, for: .vertical)

        let content = UIStackView(arrangedSubviews: [titleLabel, soldLabel, spacer, priceLabel])
        content.axis = .vertical
        content.spacing = 4
        content.isUserInteractionEnabled = false   // touches go to the card itself
        content.translatesAutoresizingMaskIntoConstraints = false
        addSubview(content)

        directionalLayoutMargins = NSDirectionalEdgeInsets(top: 12, leading: 12, bottom: 12, trailing: 12)
        NSLayoutConstraint.activate([
            content.topAnchor.constraint(equalTo: layoutMarginsGuide.topAnchor),
            content.leadingAnchor.constraint(equalTo: layoutMarginsGuide.leadingAnchor),
            content.trailingAnchor.constraint(equalTo: layoutMarginsGuide.trailingAnchor),
            content.bottomAnchor.constraint(equalTo: layoutMarginsGuide.bottomAnchor),
        ])

        // Accessibility: one element, announced as a button.
        isAccessibilityElement = true
        accessibilityTraits = .button
        accessibilityLabel = [item.title, item.formattedPrice, item.isSold ? "Sold" : nil]
            .compactMap { $0 }
            .joined(separator: ", ")
    }
}
