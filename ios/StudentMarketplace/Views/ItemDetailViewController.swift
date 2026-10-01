import UIKit

/// Detail screen for a single marketplace item.
///
/// TODO: Fetch item data from GET /items/{id} using APIClient.getItem().
/// TODO: Display title, description, price, category, seller name, date.
/// TODO: Show a "SOLD" badge if the item is sold.
/// TODO: Add a "Mark as sold" button that calls PATCH /items/{id}.
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
        loadItem()
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
                case .failure(let error):
                    self.setState(.error(error))
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
            stack.isHidden = true
            errorStack.isHidden = true
            
        case .loaded :
            spinner.stopAnimating()
            stack.isHidden = false
            errorStack.isHidden = true
            
        case .error(let error) :
            spinner.stopAnimating()
            stack.isHidden = true
            errorStack.isHidden = false
            errorLabel.text = error.localizedDescription
        }
    }
    
    // Layout
    private func setupUI() {
        stack.axis = .vertical
        stack.spacing = 12
        stack.translatesAutoresizingMaskIntoConstraints = false
        
        titleLabel.font = .preferredFont(forTextStyle: .title1)
        titleLabel.numberOfLines = 0
        descriptionLabel.numberOfLines = 0
        
        [soldBadge , titleLabel, priceLabel, categoryLabel, sellerLabel, dateLabel, descriptionLabel , soldButton]
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
        spinner.hidesWhenStopped = true
        spinner.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(spinner)
        errorLabel.numberOfLines = 0
        errorLabel.textAlignment = .center
        errorLabel.textColor = .secondaryLabel
        errorStack.axis = .vertical
        errorStack.spacing = 12
        errorStack.alignment = .center
        errorStack.isHidden = true
        errorStack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(errorStack)
        
        view.addSubview(stack)
                let guide = view.safeAreaLayoutGuide
                NSLayoutConstraint.activate([
                    stack.topAnchor.constraint(equalTo: guide.topAnchor, constant: 16),
                    stack.leadingAnchor.constraint(equalTo: guide.leadingAnchor, constant: 16),
                    stack.trailingAnchor.constraint(equalTo: guide.trailingAnchor, constant: -16),
                    spinner.centerXAnchor.constraint(equalTo: view.centerXAnchor),
                    spinner.centerYAnchor.constraint(equalTo: view.centerYAnchor),
                    errorStack.centerXAnchor.constraint(equalTo: view.centerXAnchor),
                    errorStack.centerYAnchor.constraint(equalTo: view.centerYAnchor),
                ])
    }
}
