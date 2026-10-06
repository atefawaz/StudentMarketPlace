import UIKit

/// Detail screen for a single marketplace item.
class ItemDetailViewController: UIViewController {

    /// Set by the presenting view controller before navigation.
    var itemId: Int = -1
    
    private let stack = UIStackView()
    private let titleLabel = UILabel()
    private let priceLabel = UILabel()
    private let categoryLabel = UILabel()
    private let sellerLabel = UILabel()
    private let dateLabel = UILabel()
    private let descriptionLabel = UILabel()
    private let soldBadge = UILabel()
    private let soldButton = UIButton(type: .system)
    private var currentItem: Item?
    
    private var similarItems: [Item] = []
    
    private let scrollView = UIScrollView()
    private let similarSection = UIStackView()
    private let similarTitleLabel = UILabel()
    private let similarScrollView = UIScrollView()
    private let similarStack = UIStackView()
    
    private let spinner = UIActivityIndicatorView(style: .large)
    private let errorLabel = UILabel()
    private lazy var retryButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Retry", for: .normal)
        button.addTarget(self, action: #selector(loadItem), for: .touchUpInside)
        return button
    }()
    private lazy var errorStack = UIStackView(arrangedSubviews: [errorLabel , retryButton])
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Item Detail"
        view.backgroundColor = .systemBackground
        setupUI()
        
        NotificationCenter.default.addObserver(
            self, selector: #selector(itemDidUpdate(_:)),
            name: .itemUpdated, object: nil
        )
        
        loadItem()
    }
    
    @objc private func itemDidUpdate(_ notification: Notification) {
        guard let updated = notification.userInfo?["item"] as? Item else { return }

        // This screen shows the item that changed (e.g. the older copy of A in the stack)
        if updated.id == itemId {
            populate(with: updated)
        }

        // A similar-items card shows the item that changed
        if let index = similarItems.firstIndex(where: { $0.id == updated.id }) {
            similarItems[index] = updated
            showSimilar(similarItems)
        }
    }
    
//    Loading the data
    
    @objc private func loadItem() {
            setState(.loading)
            APIClient.getItem(id: itemId) { [weak self] result in
                DispatchQueue.main.async {
                    guard let self = self else { return }
                    switch result {
                    case .success(let item):
                        self.populate(with: item)
                        self.setState(.loaded)
                        self.loadSimilarItems()
                    case .failure(let error):
                        self.setState(.error(error))
                    }
                }
            }
        }
    
    private func populate(with item : Item ) {
        currentItem = item
        titleLabel.text = item.title
        priceLabel.text = item.formattedPrice
        categoryLabel.text = "Category : \(item.category)"
        sellerLabel.text = "Sold by \(item.sellerName)"
        dateLabel.text = "Posted \(relativeDate(from: item.createdAt))"
        descriptionLabel.text = item.description ?? "No description provided ."
        soldBadge.isHidden = !item.isSold
        let isOwner = (Session.shared.currentSeller?.id == item.sellerId)
        soldButton.isHidden = !isOwner
        soldButton.setTitle(item.isSold ? "Mark as Available" : "Mark as Sold", for: .normal)
        
    }
    
    
    @objc private func soldButtonTapped() {
        guard let currentItem = currentItem else { return }
        let goingToSell = !currentItem.isSold
        let message = goingToSell ? "Mark this item as sold?" : "Mark this item as available?"
        let alert = UIAlertController(title: message, message: nil, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        alert.addAction(UIAlertAction(title: "Confirm", style: .default) { [weak self] _ in
            self?.updateSold(to: goingToSell)
        })
        present(alert, animated: true)
    }
    
    private func updateSold(to isSold: Bool) {
        APIClient.setSold(id: itemId, isSold: isSold) { [weak self] result in
            DispatchQueue.main.async {
                guard let self = self else { return }
                switch result {
                case .success(let item):
                    self.populate(with: item)     // re-draws badge + button label
                    NotificationCenter.default.post(name: .itemUpdated, object: nil, userInfo: ["item": item])
                case .failure(let error):
                    if case APIError.forbidden = error {
                        let alert = UIAlertController(
                            title: "Not allowed",
                            message: "You can only change items you posted.",
                            preferredStyle: .alert
                        )
                        alert.addAction(UIAlertAction(title: "OK", style: .default))
                        self.present(alert, animated: true)
                    } else {
                        self.setState(.error(error))
                    }
                }
            }
        }
    }
    
    
    
    // SMKT003 - TURNING TIMESTAMP INTO SOMETHING LIKE "2 HOURS AGO... "
    
    private func relativeDate(from raw : String) -> String {
        let parser = DateFormatter()
        parser.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
        parser.timeZone = TimeZone(identifier: "UTC")
        parser.locale = Locale(identifier: "en_US_POSIX")
        
        guard let date = parser.date(from: raw) else {
                    return raw
                }
                let formatter = RelativeDateTimeFormatter()
                formatter.unitsStyle = .full
                return formatter.localizedString(for: date, relativeTo: Date())

    }
    
    
    
    // SMKT-005 : Screen state
    
    private enum State {
        case loading , loaded
        case error(Error)
    }
    
    private func setState(_ state : State) {
        switch state {
        case .loading :
            spinner.startAnimating()
            scrollView.isHidden = true
            errorStack.isHidden = true
            
        case .loaded :
            spinner.stopAnimating()
            scrollView.isHidden = false
            errorStack.isHidden = true
            
        case .error(let error) :
            spinner.stopAnimating()
            scrollView.isHidden = true
            errorStack.isHidden = false
            errorLabel.text = error.localizedDescription
        }
    }
    
    // Layout
    private func setupUI() {
        // MARK: Main stack
        stack.axis = .vertical
        stack.spacing = 12
        stack.translatesAutoresizingMaskIntoConstraints = false

        titleLabel.font = .preferredFont(forTextStyle: .title1)
        titleLabel.numberOfLines = 0
        descriptionLabel.numberOfLines = 0

        [soldBadge, titleLabel, priceLabel, categoryLabel, sellerLabel, dateLabel, descriptionLabel, soldButton]
            .forEach { stack.addArrangedSubview($0) }

        soldBadge.text = " SOLD "
        soldBadge.font = .boldSystemFont(ofSize: 28)
        soldBadge.textColor = .white
        soldBadge.backgroundColor = .systemRed
        soldBadge.textAlignment = .center
        soldBadge.layer.cornerRadius = 8
        soldBadge.clipsToBounds = true
        soldBadge.isHidden = true

        soldButton.configuration = .borderedProminent()
        soldButton.addTarget(self, action: #selector(soldButtonTapped), for: .touchUpInside)

        // MARK: Similar items section (last block of the main stack)
        similarTitleLabel.text = "Similar items"
        similarTitleLabel.font = .preferredFont(forTextStyle: .title3)
        similarTitleLabel.adjustsFontForContentSizeCategory = true

        similarStack.axis = .horizontal
        similarStack.spacing = 12
        similarStack.translatesAutoresizingMaskIntoConstraints = false

        similarScrollView.showsHorizontalScrollIndicator = false
        similarScrollView.addSubview(similarStack)

        similarSection.axis = .vertical
        similarSection.spacing = 8
        similarSection.isHidden = true            // shown only once items arrive
        similarSection.addArrangedSubview(similarTitleLabel)
        similarSection.addArrangedSubview(similarScrollView)
        stack.addArrangedSubview(similarSection)

        // MARK: Vertical scroll view wrapping the main stack
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(scrollView)               // added first so spinner/error stay on top
        scrollView.addSubview(stack)

        // MARK: Spinner
        spinner.hidesWhenStopped = true
        spinner.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(spinner)

        // MARK: Error state
        errorLabel.numberOfLines = 0
        errorLabel.textAlignment = .center
        errorLabel.textColor = .secondaryLabel
        errorStack.axis = .vertical
        errorStack.spacing = 12
        errorStack.alignment = .center
        errorStack.isHidden = true
        errorStack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(errorStack)

        // MARK: Constraints
        let guide = view.safeAreaLayoutGuide
        NSLayoutConstraint.activate([
            // Scroll view: full height, respects side safe areas in landscape
            scrollView.topAnchor.constraint(equalTo: view.topAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            scrollView.leadingAnchor.constraint(equalTo: guide.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: guide.trailingAnchor),

            // Main stack inside the scroll view (16pt padding, width fixed to the screen)
            stack.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor, constant: 16),
            stack.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor, constant: -16),
            stack.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor, constant: 16),
            stack.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor, constant: -16),
            stack.widthAnchor.constraint(equalTo: scrollView.frameLayoutGuide.widthAnchor, constant: -32),

            // Horizontal cards row: scroll view sizes itself to the tallest card
            similarStack.topAnchor.constraint(equalTo: similarScrollView.contentLayoutGuide.topAnchor),
            similarStack.bottomAnchor.constraint(equalTo: similarScrollView.contentLayoutGuide.bottomAnchor),
            similarStack.leadingAnchor.constraint(equalTo: similarScrollView.contentLayoutGuide.leadingAnchor),
            similarStack.trailingAnchor.constraint(equalTo: similarScrollView.contentLayoutGuide.trailingAnchor),
            similarScrollView.frameLayoutGuide.heightAnchor.constraint(equalTo: similarScrollView.contentLayoutGuide.heightAnchor),

            // Spinner and error state, centred
            spinner.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            spinner.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            errorStack.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            errorStack.centerYAnchor.constraint(equalTo: view.centerYAnchor),
        ])
    }
    
    // MARK: - Similar items

    private func loadSimilarItems() {
        APIClient.getSimilarItems(id: itemId) { [weak self] result in
            DispatchQueue.main.async {
                // Secondary content: on failure, just don't show the section.
                guard let self = self, case .success(let items) = result else { return }
                self.showSimilar(items)
            }
        }
    }

    private func showSimilar(_ items: [Item]) {
        similarItems = items
        similarStack.arrangedSubviews.forEach { $0.removeFromSuperview() }

        for item in items {
            let card = ItemCardView(item: item)
            card.addAction(UIAction { [weak self] _ in self?.openItem(id: item.id) }, for: .touchUpInside)
            similarStack.addArrangedSubview(card)

            // ~2.2 cards visible on iPhone (hints at scrolling), capped on wide screens.
            let proportional = card.widthAnchor.constraint(equalTo: similarScrollView.frameLayoutGuide.widthAnchor,
                                                           multiplier: 0.45)
            proportional.priority = .defaultHigh
            proportional.isActive = true
            card.widthAnchor.constraint(lessThanOrEqualToConstant: 220).isActive = true
        }
        similarSection.isHidden = items.isEmpty
    }

    private func openItem(id: Int) {
        let detail = ItemDetailViewController()
        detail.itemId = id
        navigationController?.pushViewController(detail, animated: true)
    }
}
