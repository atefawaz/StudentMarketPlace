import UIKit

/// Form to create a new marketplace listing.
///
/// TODO: Add text fields for title, description, price, category, seller name.
/// TODO: Validate that required fields are not empty and price > 0.
/// TODO: POST the new item using APIClient.createItem().
/// TODO: On success, pop back to the list. On error, show an alert.
class CreateItemViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Sell an Item"
        view.backgroundColor = .systemBackground

        let placeholderLabel = UILabel()
        placeholderLabel.text = "TODO: Build the create-item form here"
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
