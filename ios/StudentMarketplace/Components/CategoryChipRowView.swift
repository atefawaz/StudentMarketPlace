import UIKit

final class CategoryChipRowView: UIView {
    
    /// Called when a chip is tapped. `nil` means "All" (no filter).
    var onCategorySelected: ((String?) -> Void)?
    
    private let scrollView = UIScrollView()
    private let stackView = UIStackView()
    private var chips: [CategoryChipButton] = []
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        setUp()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    func setCategories(_ categories: [ItemCategory]) {
        stackView.arrangedSubviews.forEach { $0.removeFromSuperview() }
        chips.removeAll()
        
        let allChip = addChip(title: "All", category: nil)
        allChip.isSelected = true
        
        for category in categories {
            addChip(title: category.name, category: category.name)
        }
    }
    
    @discardableResult
    private func addChip(title: String, category: String?) -> CategoryChipButton {
        let chip = CategoryChipButton(title: title)
        chip.addAction(UIAction { [weak self, weak chip] _ in
                guard let self, let chip, !chip.isSelected else { return }
                self.select(chip)
                self.onCategorySelected?(category)
            }, for: .touchUpInside
        )
        
        chips.append(chip)
        stackView.addArrangedSubview(chip)
        return chip
    }
    
    private func select(_ selectedChip: CategoryChipButton) {
        chips.forEach{ $0.isSelected = ($0 == selectedChip) }
        
        let frame = selectedChip.convert(selectedChip.bounds, to: scrollView)
        scrollView.scrollRectToVisible(frame.insetBy(dx: -16, dy: 0), animated: true)
    }
    
    private func setUp() {
        scrollView.showsHorizontalScrollIndicator = false
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        addSubview(scrollView)
        
        stackView.axis = .horizontal
        stackView.spacing = 8
        stackView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.addSubview(stackView)
        
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: topAnchor),
            scrollView.bottomAnchor.constraint(equalTo: bottomAnchor),
            scrollView.leadingAnchor.constraint(equalTo: safeAreaLayoutGuide.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: safeAreaLayoutGuide.trailingAnchor),

            stackView.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor, constant: 8),
            stackView.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor, constant: -8),
            stackView.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor, constant: 16),
            stackView.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor, constant: -16),

            scrollView.frameLayoutGuide.heightAnchor.constraint(equalTo: scrollView.contentLayoutGuide.heightAnchor)
        ])
    }
}
