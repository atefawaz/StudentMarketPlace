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
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Item Detail"
        view.backgroundColor = .systemBackground
        setupUI()
        loadItem()
    }
    
//    Loading the data
    
    private func loadItem() {
            APIClient.getItem(id: itemId) { [weak self] result in
                DispatchQueue.main.async {
                    guard let self = self else { return }
                    switch result {
                    case .success(let item):
                        self.populate(with: item)
                    case .failure(let error):
                        print("Failed to load item: \(error)")
                    }
                }
            }
        }
    
    private func populate(with item : Item ) {
        titleLabel.text = item.title
        priceLabel.text = item.formattedPrice
        categoryLabel.text = "Category : \(item.category)"
        sellerLabel.text = "Sold by \(item.sellerName)"
        dateLabel.text = "Posted \(relativeDate(from: item.createdAt))"
        descriptionLabel.text = item.description ?? "No description provided ."
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
    
    // Layout
    private func setupUI() {
        stack.axis = .vertical
        stack.spacing = 12
        stack.translatesAutoresizingMaskIntoConstraints = false
        
        titleLabel.font = .preferredFont(forTextStyle: .title1)
        titleLabel.numberOfLines = 0
        descriptionLabel.numberOfLines = 0
        
        [titleLabel, priceLabel, categoryLabel, sellerLabel, dateLabel, descriptionLabel]
                    .forEach { stack.addArrangedSubview($0) }
        
        
        view.addSubview(stack)
                let guide = view.safeAreaLayoutGuide
                NSLayoutConstraint.activate([
                    stack.topAnchor.constraint(equalTo: guide.topAnchor, constant: 16),
                    stack.leadingAnchor.constraint(equalTo: guide.leadingAnchor, constant: 16),
                    stack.trailingAnchor.constraint(equalTo: guide.trailingAnchor, constant: -16),
                ])
    }
}
