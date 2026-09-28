import UIKit

/// Displays the list of marketplace items in a UITableView.
class ItemListViewController: UITableViewController {

    private var items: [Item] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Marketplace"
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "ItemCell")

        // "+" button to create a new item
        navigationItem.rightBarButtonItem = UIBarButtonItem(
            barButtonSystemItem: .add,
            target: self,
            action: #selector(openCreateItem)
        )
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        loadItems()
    }

    // MARK: - Data loading

    private func loadItems() {
        APIClient.getItems { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let items):
                    self?.items = items
                    self?.tableView.reloadData()
                case .failure(let error):
                    let alert = UIAlertController(
                        title: "Error",
                        message: error.localizedDescription,
                        preferredStyle: .alert
                    )
                    alert.addAction(UIAlertAction(title: "OK", style: .default))
                    self?.present(alert, animated: true)
                }
            }
        }
    }

    // MARK: - UITableViewDataSource

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        items.count
    }

    override func tableView(_ tableView: UITableView,
                            cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "ItemCell", for: indexPath)
        let item = items[indexPath.row]

        var config = cell.defaultContentConfiguration()
        config.text = item.title
        config.secondaryText = "\(item.formattedPrice) — \(item.category)"
        if item.isSold {
            config.secondaryText = "[SOLD] \(config.secondaryText ?? "")"
        }
        cell.contentConfiguration = config
        cell.accessoryType = .disclosureIndicator
        cell.alpha = item.isSold ? 0.5 : 1.0
        return cell
    }

    // MARK: - UITableViewDelegate

    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        let item = items[indexPath.row]
        let detailVC = ItemDetailViewController()
        detailVC.itemId = item.id
        navigationController?.pushViewController(detailVC, animated: true)
    }

    // MARK: - Actions

    @objc private func openCreateItem() {
        let createVC = CreateItemViewController()
        navigationController?.pushViewController(createVC, animated: true)
    }
}
