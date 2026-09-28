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

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Item Detail"
        view.backgroundColor = .systemBackground

        let placeholderLabel = UILabel()
        placeholderLabel.text = "TODO: Load item #\(itemId) details here"
        placeholderLabel.textAlignment = .center
        placeholderLabel.textColor = .secondaryLabel
        placeholderLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(placeholderLabel)

        NSLayoutConstraint.activate([
            placeholderLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            placeholderLabel.centerYAnchor.constraint(equalTo: view.centerYAnchor),
        ])
    }
}
